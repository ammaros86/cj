class FakeHeaderGenerator:

    def __init__(self, type_collector):
        self.type_collector = type_collector

    def _to_var_name(self, name):
        return name.lower()

    def generate(self, cls, original_header, instance_count, known_types):

        name = cls["name"]
        var_name = self._to_var_name(name)

        # ✅ normale Typen
       # types = self.type_collector.collect(original_header)


 
        use_array = instance_count > 1

        lines = []
        lines.append('#include "GeneratedTypes.h"\n')

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------
        lines.append("#pragma once")
        lines.append(f'#include "I{name}.h"\n')

        # --------------------------------------------------
        # NORMAL TYPES (enum / struct / typedef)
        # --------------------------------------------------
       # if types:
         #   lines.append("// === GENERATED TYPES ===")
          #  for t in types:
          #      lines.append(t)
         #   lines.append("")

        # --------------------------------------------------
        # SCOPED TYPES
        # --------------------------------------------------
        #  if scoped_types:
          #    lines.append("// === SCOPED TYPES ===")
          #    for t in scoped_types:
           #       lines.append(t)
           #   lines.append("")

        # --------------------------------------------------
        # GLOBAL POINTERS
        # --------------------------------------------------
        if use_array:
            lines.append(f"extern I{name}* {var_name}Mocks[{instance_count}];")
            lines.append(f"extern int {var_name}_mock_instances;\n")
        else:
            lines.append(f"extern I{name}* {var_name}Mock;\n")

        # --------------------------------------------------
        # CLASS
        # --------------------------------------------------
        lines.append(f"class {name} {{")
        lines.append("public:")

        if use_array:
            lines.append(f"    {name}() {{ id = {var_name}_mock_instances++; }}")

        # --------------------------------------------------
        # METHODS
        # --------------------------------------------------
        for m in cls["methods"]:

            ret = m["return"]

            params = []
            names = []

            for ptype, pname in m["params"]:
                params.append(f"{ptype} {pname}")
                names.append(pname)

            # call forwarding
            if use_array:
                call = f"{var_name}Mocks[id]->{m['name']}({', '.join(names)})"
            else:
                call = f"{var_name}Mock->{m['name']}({', '.join(names)})"

            lines.append(f"    inline {ret} {m['name']}({', '.join(params)}) {{")

            if ret != "void":
                lines.append(f"        return {call};")
            else:
                lines.append(f"        {call};")

            lines.append("    }")

        # --------------------------------------------------
        # PRIVATE
        # --------------------------------------------------
        if use_array:
            lines.append("\nprivate:")
            lines.append("    int id;")

        lines.append("};")

        return "\n".join(lines)
 
