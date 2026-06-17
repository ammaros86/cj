 import re

class CppAnalyzer:

    def count_instantiations(self, cpp_path, class_name):
        count = 0

        with open(cpp_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        pattern = rf'\b{class_name}\s+\w+'
        matches = re.findall(pattern, content)

        return len(matches)
