import re

class TypeCollector:



    def _is_standard_type(self, t):
        standard = {
            "int", "float", "double", "bool", "char",
            "uint8_t", "uint16_t", "uint32_t", "uint64_t",
            "size_t", "void"
        }
        return t in standard


    def _build_simple_struct(self, name):
        return f"struct {name} {{}};"

    def _collect_class_names(self, cls, prefix=""):
        names = set()

        current_name = cls["name"]

        if prefix:
            full_name = f"{prefix}::{current_name}"
        else:
            full_name = current_name

        # ✅ nur Klassennamen speichern
        names.add(current_name)

        # ✅ auch scoped Variante (wichtig!)
        names.add(full_name)

        # ✅ rekursiv nested classes
        for inner in cls.get("inner_classes", []):
            names.update(self._collect_class_names(inner, full_name))

        return names


    def collect_global_types(self, header_map, known_types):

        generated = set()

        for header, classes in header_map.items():

            # --------------------------------------------------
            # ✅ 1. FILE SCAN (A::B::C::D)
            # --------------------------------------------------
            with open(header, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            matches = re.findall(r'\b[\w:]+\b', content)

            for match in matches:

                clean = self._clean_type(match)
                typename = clean.split("::")[-1]

                if typename in known_types:
                    continue

                generated.add(self._build_simple_struct(typename))

            # --------------------------------------------------
            # ✅ 2. METHODS (wie bisher)
            # --------------------------------------------------
            for cls in classes:
                for m in cls["methods"]:

                    types_to_check = [m["return"]]

                    for ptype, _ in m["params"]:
                        types_to_check.append(ptype)

                    for t in types_to_check:

                        clean = self._clean_type(t)

                        # ✅ mehrere Typen extrahieren (WICHTIG!)
                        tokens = re.findall(r'\b[\w:]+\b', clean)

                        for token in tokens:

                            # ✅ Standard skip
                            if self._is_standard_type(token):
                                continue

                            # ✅ std ignorieren
                            if token.startswith("std"):
                                continue

                            # ✅ scoped oder normal
                            if "::" in token:
                                typename = token.split("::")[-1]
                            else:
                                typename = token

                            # ✅ bekannte skip
                            if typename in known_types:
                                continue

                            generated.add(self._build_simple_struct(typename))


            # --------------------------------------------------
            # ✅ 3. INNER CLASSES 💥 (NEU)
            # --------------------------------------------------
            for cls in classes:

                names = self._collect_class_names(cls)

                for n in names:
                    typename = n.split("::")[-1]

                  #  if typename in known_types:
                       # continue

                    # optional: standard types skip
                    if self._is_standard_type(typename):
                        continue

                    generated.add(self._build_simple_struct(typename))

        return generated
    
    



    def collect_all_known_types(self, header_map):

        known_types = set()

        for header, classes in header_map.items():

            for cls in classes:
                names = self._collect_class_names(cls)

                for n in names:
                    short = n.split("::")[-1]

                    known_types.add(short)
                    known_types.add(n)   # ✅ scoped name auch speichern

            # ✅ typedef / enum / struct
            types = self.collect(header)

            for t in types:
                name = self._extract_typename(t)
                if name:
                    known_types.add(name)

        return known_types



    def _extract_typename(self, type_def):

        # typedef int X;
        m = re.search(r'typedef\s+.*?\s+(\w+)\s*;', type_def)
        if m:
            return m.group(1)

        # struct X
        m = re.search(r'struct\s+(\w+)', type_def)
        if m:
            return m.group(1)

        # enum X
        m = re.search(r'enum\s+(\w+)', type_def)
        if m:
            return m.group(1)

        return None


    def collect_scoped_types(self, cls, known_types):

        generated = []
        seen = set()

        for m in cls["methods"]:

            types_to_check = [m["return"]]

            for ptype, _ in m["params"]:
                types_to_check.append(ptype)

            for t in types_to_check:

                if "::" not in t:
                    continue

                clean = self._clean_type(t)

                parts = clean.split("::")

                typename = parts[-1]
                namespaces = parts[:-1]

                # ✅ WICHTIGER FIX!!!
                if typename in known_types:
                    continue   # 👉 NICHT generieren!

                key = tuple(parts)
                if key in seen:
                    continue

                seen.add(key)

                code = self._build_namespace_chain(namespaces, typename)
                generated.append(code)

        return generated

    def _clean_type(self, t):

        # remove qualifiers
        t = re.sub(r'\bconst\b', '', t)
        t = re.sub(r'\bvolatile\b', '', t)

        # remove pointer/reference
        t = t.replace("*", "")
        t = t.replace("&", "")

        # remove templates (optional später)
        t = re.sub(r'<.*?>', '', t)

        # remove extra spaces
        t = " ".join(t.split())

        return t.strip()
 
    def _build_namespace_chain(self, namespaces, typename):
        lines = []

        for ns in namespaces:
            lines.append(f"namespace {ns} {{")

        lines.append(f"struct {typename} {{}};")

        for _ in namespaces:
            lines.append("}")

        return "\n".join(lines)


    def collect(self, header_path):
        types = []

        with open(header_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # ✅ Kommentare entfernen (optional)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//.*', '', content)

        # ✅ ENUMS
        enums = re.findall(r'enum\s+\w+\s*\{[^}]*\};', content, re.DOTALL)
        types.extend(enums)

        # ✅ STRUCTS
        structs = re.findall(r'struct\s+\w+\s*\{[^}]*\};', content, re.DOTALL)
        types.extend(structs)

        # ✅ TYPEDEF
        typedefs = re.findall(r'typedef\s+[^;]+;', content)
        types.extend(typedefs)

        # ✅ USING
        using = re.findall(r'using\s+\w+\s*=\s*[^;]+;', content)
        types.extend(using)

        return types
