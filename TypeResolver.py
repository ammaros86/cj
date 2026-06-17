class TypeResolver:
    def __init__(self, parsed_classes):
        """
        parsed_classes = LISTE von class-dicts
        """
        self.known_types = set()

        # 🔥 REKURSIV alle Klassen sammeln
        self._collect_types(parsed_classes)

    # --------------------------------
    # Rekursiv alle Klassennamen sammeln
    # --------------------------------
    def _collect_types(self, classes):
        for cls in classes:
            name = cls.get("name")
            if name:
                self.known_types.add(name)

            # 🔥 Nested Klassen
            inner = cls.get("inner_classes", [])
            self._collect_types(inner)

    # --------------------------------
    # Standard Typen
    # --------------------------------
    def is_standard(self, t):
        standard = {
            "int", "char", "char*", "uint8_t", "uint16_t", "uint32_t", "uint64_t",
            "bool", "void",
            "float", "double"
        }
        return t in standard

    # --------------------------------
    # Mapping
    # --------------------------------
    def map_type(self, t):
        t = t.strip()

        # ✅ Keywords entfernen
        t = t.replace("static", "")
        t = t.replace("inline", "")
        t = t.replace("virtual", "")
        t = t.replace("const", "")

        t = t.strip()

        # ✅ pointer/reference merken
        
        is_ptr = "*" in t or "&" in t
        base = t.strip()
 

        STANDARD = {
            "int": "uint32_t",
            "char": "uint8_t",
            "bool": "bool",
            "float": "float",
            "double": "double",
            "void": "void",
            "uint32_t": "uint32_t",
            "uint8_t": "uint8_t"
        }

        if base in STANDARD:
            return STANDARD[base]

        # ✅ custom type
        if base in self.known_types:
            return "uint32_t"

        # ✅ pointer fallback
        if is_ptr:
            return base

        return "uint32_t"

    # --------------------------------
    # Wrapper Cast
    # --------------------------------
    def cast_to_original(self, t, var):
        return f"static_cast<{t}>({var})"
