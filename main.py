import json

from headerScan import HeaderScanner
from DependencyEngine import DependencyEngine


# -----------------------------------------
# Config laden
# -----------------------------------------
def load_config(path):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------------------
# MAIN
# -----------------------------------------
def main():
    config = load_config("config.json")

    root_header = config["root_header"]
    cpp_file = config["cpp_file"]
    include_dirs = config["include_dirs"]
    exclude_dirs = config["exclude_dirs"]

    # -----------------------------------------
    # 1. Header Scanner
    # -----------------------------------------
    scanner = HeaderScanner(include_dirs, exclude_dirs)
    scanner.run(root_header)

    # -----------------------------------------
    # 2. Dependency Engine
    # -----------------------------------------
    engine = DependencyEngine(scanner, include_dirs)

    result = engine.run(root_header, cpp_file)

    # -----------------------------------------
    # 3. Ausgabe
    # -----------------------------------------
    print("\n📦 Strategie pro Header:")
    for header, strategy in result["strategies"].items():
        print(f"{header} -> {strategy}")

    # -----------------------------------------
    # 4. Zeilenanalyse CPP
    # -----------------------------------------
    print("\n📄 CPP Line Mapping:")
    for line_no, data in result["cpp_line_map"].items():
        print(f"{line_no}: {data['line']}")
        print(f"   -> {data['headers']}")

    # -----------------------------------------
    # 5. Zeilenanalyse Header
    # -----------------------------------------
    print("\n📄 Header Line Mapping:")
    for line_no, data in result["header_line_map"].items():
        print(f"{line_no}: {data['line']}")
        print(f"   -> {data['headers']}")

    # -----------------------------------------
    # 6. User Types
    # -----------------------------------------
    print("\n🧩 Erkannte User Types:")
    for root, nested in result["user_types"].items():
        print(f"{root} -> {nested}")


# -----------------------------------------
if __name__ == "__main__":
    main()
