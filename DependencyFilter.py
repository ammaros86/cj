import os

class DependencyFilter:

    def __init__(self, scanner):
        self.scanner = scanner   # ✅ brauchst du für find_header()

    def filter(self, cpp_file, header_map, root_header):

        print("\n🔎 Dependency Filter läuft...")

        # ✅ includes aus cpp holen
        includes = self.scanner.extract_includes(cpp_file)

        relevant_headers = set()

        # ✅ nur gültige Header übernehmen
        for inc in includes:
            found = self.scanner.find_header(inc)

            if found:
                print(f"✅ Relevant: {inc} -> {found}")
                relevant_headers.add(found)
            else:
                print(f"⚠️ Nicht gefunden: {inc}")

        # ✅ immer eigene klasse hinzufügen
        relevant_headers.add(root_header)

        # ✅ filtern
        filtered_map = {}

        for h, classes in header_map.items():
            if h in relevant_headers:
                filtered_map[h] = classes

        print("\n✅ Gefilterte Header:")
        for h in filtered_map:
            print(" -", h)

        return filtered_map
