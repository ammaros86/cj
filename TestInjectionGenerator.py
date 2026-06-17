import os

class TestInjectionGenerator:

    def generate(self, includes):
        test_includes = []
        prod_includes = []

        for inc in includes:

            base = os.path.basename(inc)

            if not base.endswith(".h"):
                continue

            name = base.replace(".h", "")

            # ✅ Nur Klassen mit Großbuchstaben
            if base[0].isupper():
                test_includes.append(
                    f'#include "tests/mocks/{name}Test.h"'
                )
                prod_includes.append(f'#include <{base}>')
            else:
                prod_includes.append(f'#include <{base}>')

        lines = []

        lines.append("#ifdef _TEST_\n")

        for inc in test_includes:
            lines.append(inc)

        lines.append("\n// Logging deaktivieren")
        lines.append("inline void LOG_INFO_ARG(...) {}")
        lines.append("inline void LOG_ERROR_ARG(...) {}")
        lines.append("inline void EXCEPTION_LOG(...) {}")
        lines.append("inline void LOG_ERROR(...) {}")
        lines.append("inline void LOG_INFO(...) {}")

        lines.append("\n#else\n")

        for inc in prod_includes:
            lines.append(inc)

        lines.append("\n#endif")

        return "\n".join(lines)
