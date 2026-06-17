import os
import re



class HeaderScanner:
    def __init__(self, include_dirs, exclude_dirs=None):
        self.include_dirs = include_dirs
        self.exclude_dirs = exclude_dirs or []
        self.visited = set()
        self.header_index = {}

        self._build_index()

    # -----------------------------------------
    # Prüfen ob Verzeichnis ausgeschlossen ist
    # -----------------------------------------
    def _is_excluded(self, path):
        for ex in self.exclude_dirs:
            if path.startswith(ex):
                return True
        return False

    # -----------------------------------------
    # Nur Header mit Großbuchstaben am Anfang
    # -----------------------------------------
    def _is_valid_header(self, filename):
        if not (filename.endswith(".h") or filename.endswith(".hpp")):
            return False

        if not filename:
            return False

        return filename[0].isupper()

    # -----------------------------------------
    # Index bauen (mit Filter + exclude)
    # -----------------------------------------
    def _build_index(self):
        print("🔎 Indexing header files...")

        for base in self.include_dirs:
            for root, dirs, files in os.walk(base):

                # exclude check
                if self._is_excluded(root):
                    continue

                for f in files:
                    if self._is_valid_header(f):
                        full_path = os.path.join(root, f)
                        
                        full_path = os.path.normpath(full_path)
                        full_path = full_path.replace("\\", "/")

                        self.header_index[f] = full_path

        print(f"✅ {len(self.header_index)} gültige Header indexed.\n")

    # -----------------------------------------
    # Includes extrahieren ("" + <>)
    # -----------------------------------------
    def extract_includes(self, file_path):
        includes = []

        pattern = re.compile(r'#include\s*[<"]([^">]+)[">]')

        print(f"\n📄 Lese Datei: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

                matches = pattern.findall(content)

                for inc in matches:
                    print(f"  ➜ include: {inc}")
                    includes.append(inc)

        except Exception as e:
            print(f"❌ Fehler beim Lesen: {file_path}")
            print(e)

        return includes

    # -----------------------------------------
    # Header finden
    # -----------------------------------------
    def find_header(self, header_name):
        base = os.path.basename(header_name)
        return self.header_index.get(base, None)

    # -----------------------------------------
    # Rekursive Suche
    # -----------------------------------------
    def scan_recursive(self, header_path):
        if not os.path.exists(header_path):
            print(f"❌ Datei nicht gefunden: {header_path}")
            return

        if header_path in self.visited:
            return

        self.visited.add(header_path)
        print(f"🔍 {header_path}")

        includes = self.extract_includes(header_path)

        for inc in includes:

            # nur Header mit Großbuchstaben weiter verfolgen
            base = os.path.basename(inc)

            if not base or not base[0].isupper():
                continue

            found = self.find_header(inc)

            if found:
                self.scan_recursive(found)
            else:
                print(f"⚠️ Nicht gefunden: {inc}")

    # -----------------------------------------
    # RUN
    # -----------------------------------------
    def run(self, root_header):
        self.visited.clear()

        self.scan_recursive(root_header)

        print("\n✅ Ergebnis:")
        for h in self.visited:
            print(" -", h)

        return self.visited





