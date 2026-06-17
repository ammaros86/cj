class MockGenerator:

    def generate(self, cls):
        name = cls["name"]

        lines = []
        lines.append("#pragma once")
        lines.append("#include <gmock/gmock.h>")
        lines.append(f'#include "I{name}.h"\n')

        lines.append(f"class Mock{name} : public I{name} {{")
        lines.append("public:")

        for m in cls["methods"]:
            ret = m["return"]

            param_types = []

            for ptype, pname in m["params"]:
                param_types.append(ptype)

            lines.append(
                f"    MOCK_METHOD({ret}, {m['name']}, ({', '.join(param_types)}), (override));"
            )

        lines.append("};")

        return "\n".join(lines)
 
