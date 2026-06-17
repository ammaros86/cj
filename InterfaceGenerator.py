class InterfaceGenerator:
    def __init__(self, type_resolver):
        self.tr = type_resolver

    def generate(self, cls, indent=0):
        tab = "    " * indent
        lines = []

        lines.append(f"{tab}class I{cls['name']} {{")
        lines.append(f"{tab}public:")
        lines.append(f"{tab}    virtual ~I{cls['name']}() = default;\n")

        for m in cls["methods"]:
            ret = self.tr.map_type(m["return"])
            if m["original_name"] == "getInstance":
                continue
            params = []
            for ptype, pname in m["params"]:
                params.append(f"{self.tr.map_type(ptype)} {pname}")

            lines.append(
                f"{tab}    virtual {ret} {m['name']}({', '.join(params)}) = 0;"
            )

        # ✅ nested classes
        for inner in cls["inner_classes"]:
            lines.append("")
            lines.append(self.generate(inner, indent + 1))

        lines.append(f"{tab}}};")

        return "\n".join(lines)
 
 
