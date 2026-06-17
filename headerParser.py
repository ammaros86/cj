import re



 

class ClassDef:
    def __init__(self, name):
        self.name = name
        self.methods = []
        self.inner_classes = []

    def to_dict(self):
        return {
            "name": self.name,
            "methods": [
                {
                    "name": m.name,
                    "original_name": m.original_name,
                    "return": m.ret,
                    "params": m.params
                }
                for m in self.methods
            ],
            "inner_classes": [
                inner.to_dict() for inner in self.inner_classes
            ]
        }

class Method:
    def __init__(self, ret, name, original_name, params):
        self.ret = ret
        self.name = name
        self.original_name = original_name
        self.params = params

class HeaderParser:
    def __init__(self, filepath):
        self.filepath = filepath

    # -----------------------------------------
    # Kommentare entfernen
    # -----------------------------------------
    def remove_comments(self, text):
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        text = re.sub(r'//.*', '', text)
        return text

    # -----------------------------------------
    # Parser
    # -----------------------------------------
    def _extract_outer_public(self, body):
        """
        Entfernt inner classes NUR für Methoden-Parsing
        """
        result = ""
        i = 0
        depth = 0

        while i < len(body):
            if body.startswith("class", i):
                # skip inner class komplett
                while i < len(body) and body[i] != "{":
                    i += 1

                if i == len(body):
                    break

                depth = 1
                i += 1

                while i < len(body) and depth > 0:
                    if body[i] == "{":
                        depth += 1
                    elif body[i] == "}":
                        depth -= 1
                    i += 1

                # skip ';'
                while i < len(body) and body[i] != ";":
                    i += 1
                i += 1

            else:
                result += body[i]
                i += 1

        return result



    def _normalize_type(self, ptype):
        ptype = ptype.replace("const", "")
        ptype = ptype.replace("&", "")
        ptype = ptype.replace("*", "ptr")
        ptype = ptype.strip()

        # Leerzeichen entfernen

        
        if "::" in ptype:
                ptype = ptype.split("::")[-1]
        if "=" in ptype:
            ptype = ptype.split("=")[-1]
        ptype = ptype.strip()
        ptype = ptype.replace(" ", "_")
        return ptype


    def _build_suffix(self, params):
        if not params:
            return "void"

        parts = []
        for ptype, _ in params:
            cleaned = self._normalize_type(ptype)
            parts.append(cleaned)

        return "_".join(parts)



    def resolve_overloads(self, cls):
        name_map = {}

        # Gruppieren
        for m in cls.methods:
            name_map.setdefault(m.name, []).append(m)

        new_methods = []

        for name, methods in name_map.items():
            if "check" in name:
                print("start")
            if len(methods) == 1:
                new_methods.append(methods[0])
                continue

            # Konflikt → Namen anpassen
            for m in methods:
                suffix = self._build_suffix(m.params)
                m.name = f"{m.name}_{suffix}"
                m.original_name = m.original_name
                new_methods.append(m)

        cls.methods = new_methods

    
    def parse_classes(self, content):
        classes = []
       
        
        class_pattern = re.compile(r'\bclass\s+(\w+)\s*(?:[:\w\s,<>\*]*)?\{')


        pos = 0

        while True:
            match = class_pattern.search(content, pos)

            if not match:
                break

            class_name = match.group(1)
            start = match.end()

            # ✅ Brace Matching
            brace_count = 1
            i = start

            while i < len(content) and brace_count > 0:
                if content[i] == "{":
                    brace_count += 1
                elif content[i] == "}":
                    brace_count -= 1
                i += 1
            full_body = content[start:i - 1]

            body = content[start:i - 1]
            body = self._extract_outer_public(body)
            cls = ClassDef(class_name)

            # Methoden
            self._parse_methods(body, cls)
            self.resolve_overloads(cls)
            # Nested
            cls.inner_classes = self.parse_classes(full_body)

            classes.append(cls)

            print("==> parse cls:", cls.name)

            # 🔥 WICHTIGER FIX
            pos = i
        return classes



    def parse(self):
        with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        content = self.remove_comments(content)

        classes = self.parse_classes(content)

        # 🔥 OPTIONAL: direkt als dict zurückgeben
        return [cls.to_dict() for cls in classes]


    # -----------------------------------------
    # Methoden extrahieren
    # -----------------------------------------
    def _parse_methods(self, body, cls):
        # nur public section nehmen
        public_match = re.search(
            r'public:(.*?)(private:|protected:|$)',
            body,
            re.DOTALL
        )

        if not public_match:
            return

        public_body = public_match.group(1)

        # Methoden Pattern

 
        method_pattern = re.compile(
            r'(?:virtual\s+|inline\s+|static\s+)?'   # optional keywords
            r'([\w:\<\>\*&\s]+?)\s+'                 # return type
            r'(\w+)\s*'                             # name
            r'\(([^()]*)\)\s*'                      # parameters
            r'(?:const)?\s*'                        # optional const
            r'(?:override)?\s*'                     # optional override
            r'(?:noexcept)?\s*'                     # optional noexcept
            r'(?:\{[^}]*\})?'                       # ✅ inline function body (NEU!)
            r'\s*;?'
        )


        # ✅ mehrere public Blöcke berücksichtigen
        public_sections = re.findall(
            r'public\s*:\s*(.*?)(?=private\s*:|protected\s*:|public\s*:|$)',
            body,
            re.DOTALL
        )

        if not public_sections:
            print(f"⚠️ Kein public gefunden in {cls.name}")
            return

        for public_body in public_sections:

            print(f"\n🔎 Analysiere public in {cls.name}:")
            # print(public_body)  # optional debug

            for m in method_pattern.finditer(public_body):

                ret = m.group(1).strip()
                name = m.group(2).strip()
                original_name = m.group(2).strip()
                params = m.group(3).strip()

                print(f"-> Methode erkannt: {name}")

                parsed_params = self._parse_params(params)

                cls.methods.append(Method(ret, name, original_name, parsed_params))


    # -----------------------------------------
    # Parameter splitten
    # -----------------------------------------
    def _parse_params(self, param_str):
        params = []
 
        if not param_str.strip():
            return params

        for p in param_str.split(","):
            parts = p.strip().split()

            if "=" in p:
                    p = p.split("=", 1)[0].strip()

            parts = p.split()

            if len(parts) >= 2:
                pname = parts[-1]
                ptype = " ".join(parts[:-1])
                params.append((ptype, pname))


        return params
