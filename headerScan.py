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
        normalized_path = os.path.normpath(path).replace("\\", "/")
        
        for ex in self.exclude_dirs:
            # Falls in der JSON kein "/" am Ende war, hängen wir es für den Test an
            ex_with_slash = ex if ex.endswith("/") else ex + "/"
            
            # Jetzt prüfen wir, ob der Pfad exakt übereinstimmt oder ein Unterordner ist
            if normalized_path == ex or normalized_path.startswith(ex_with_slash):
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
                
                # 1. Modifiziere 'dirs' in-place, um ausgeschlossene Ordner komplett zu überspringen
                # Das verhindert, dass os.walk überhaupt in diese Unterordner hineinschaut.
                dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]

                # 2. Falls der aktuelle Root-Ordner selbst ausgeschlossen ist (z.B. der Base-Ordner selbst)
                if self._is_excluded(root):
                    continue

                for f in files:
                    if self._is_valid_header(f):
                        full_path = os.path.join(root, f)
                        full_path = os.path.normpath(full_path).replace("\\", "/")

                        # Optionale Warnung, falls ein Header-Name doppelt im Projekt existiert
                        if f in self.header_index and self.header_index[f] != full_path:
                            print(f"⚠️ Warning: Duplicate header '{f}'. Overwriting {self.header_index[f]} with {full_path}")

                        self.header_index[f] = full_path

            print(f"✅ {len(self.header_index)} gültige Header indexed.\n")

    # -----------------------------------------
    # Includes extrahieren ("" + <>)
    # -----------------------------------------
    def extract_includes(self, file_path):
        includes = []
        # Erlaubt optionale Spaces VOR dem '#' für maximale Robustheit
        pattern = re.compile(r'^\s*#include\s*[<"]([^">]+)[">]', re.MULTILINE)

        print(f"\n📄 Reading file: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1. Kommentare entfernen, um fehlerhafte Includes zu vermeiden
            # Entfernt Blockkommentare /* ... */
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # Entfernt Zeilenkommentare // ...
            content = re.sub(r'//.*', '', content)

            # 2. Jetzt erst nach echten Includes suchen
            matches = pattern.findall(content)

            for inc in matches:
                print(f"  ➜ include: {inc}")
                includes.append(inc)

        except Exception as e:
            print(f"❌ Error reading file: {file_path}")
            print(e)

        return includes

    # -----------------------------------------
    # Header finden
    # -----------------------------------------
 

    def find_header(self, header_name):
        # Formatieren für einheitliche Slashes (z.B. "core/Logger.h")
        clean_include = os.path.normpath(header_name).replace("\\", "/")
        base = os.path.basename(clean_include)

        # 1. Wenn die Datei gar nicht im Index existiert, direkt abbrechen
        if base not in self.header_index:
            return None

        # 2. Wenn es ein Dictionary von Listen wäre, müsste man alle prüfen.
        # Da dein aktueller Index nur einen String speichert, holen wir den Pfad:
        indexed_path = self.header_index[base]

        # 3. Validieren, ob der Pfad auch wirklich zum Include-Ordner passt.
        # Wir prüfen, ob der indizierte Pfad mit dem gesuchten Include endet.
        # Beispiel: "C:/project/src/core/Logger.h" endet mit "core/Logger.h"
        if indexed_path.endswith(clean_include):
            return indexed_path

        # Falls der Name zwar passt, aber in einem völlig falschen Ordner liegt
        print(f"⚠️ Path mismatch: Found '{base}' at '{indexed_path}', but expected path like '{clean_include}'")
        return None
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
    def run(self, root_header, clear_visited=True):
        self.visited.clear()

        if clear_visited:
            self.visited.clear()
        self.scan_recursive(root_header)

        print("\n✅ Ergebnis:")
        for h in self.visited:
            print(" -", h)

        return self.visited





