from headerScan import HeaderScanner
from headerParser import HeaderParser
from TypeResolver import TypeResolver
from InterfaceGenerator import InterfaceGenerator
from FakeHeaderGenerator import FakeHeaderGenerator
from MockGenerator import MockGenerator
from TestInjectionGenerator import TestInjectionGenerator
from CppAnalyzer import CppAnalyzer
from DependencyFilter import DependencyFilter

from TypeCollector import TypeCollector

import json
import os


def load_config(path):
    with open(path) as f:
        return json.load(f)

def getAllHeaders():

    # ✅ Step 1: Header sammeln
    scanner = HeaderScanner(
        config["include_dirs"],
        config.get("exclude_dirs", [])
    )

    all_headers = scanner.run(config["root_header"])

    # ✅ Step 2: Header parsen
    header_map = {}

    for header in all_headers:
        parser = HeaderParser(header)
        classes = parser.parse()  # ✅ gibt jetzt dict zurück
        header_map[header] = classes


    # ✅ Dependency Filter
    dep_filter = DependencyFilter(scanner)

    header_map = dep_filter.filter(
        config["root_header"],
        header_map,
        config["root_header"]
    )
    return header_map


if __name__ == "__main__":
    config = load_config("config.json")

    header_map = {}
    header_map = getAllHeaders()

    # ✅ Resolver
    all_classes = []
    for classes in header_map.values():
        all_classes.extend(classes)

    resolver = TypeResolver(all_classes)

    # ✅ Generatoren
    #iface_gen = InterfaceGenerator(resolver)
    type_collector = TypeCollector()
    known_types = type_collector.collect_all_known_types(header_map)
    



def foo():
    append_list = []
    base_output = "generated"
    types_path = os.path.join(base_output, "GeneratedTypes.h")

    
    generated_types = type_collector.collect_global_types(
        header_map,
        known_types
    )


    if os.path.exists(types_path):

        with open(types_path, "r") as f:
            existing = f.read()

        for t in generated_types:
            if t not in existing:
                append_list.append(t)

        if append_list:
            with open(types_path, "a") as f:
                for t in append_list:
                    f.write(t + "\n")

    else:
        with open(types_path, "w", encoding="utf-8") as f:
            f.write("#pragma once\n\n")
            f.write("// === AUTO GENERATED TYPES ===\n\n")

            for t in generated_types:
                f.write(t + "\n")

    print(f"✅ GeneratedTypes: {types_path}")

    fake_gen = FakeHeaderGenerator(type_collector)
    mock_gen = MockGenerator()
    test_inject_gen = TestInjectionGenerator()


    # ✅ Output Ordner

    base_output = "generated"

    iface_dir = os.path.join(base_output, "interfaces")
    fake_dir = os.path.join(base_output, "fakes")
    mock_dir = os.path.join(base_output, "mocks")

    os.makedirs(iface_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)
    os.makedirs(mock_dir, exist_ok=True)

    types_path = os.path.join(base_output, "GeneratedTypes.h")

    cpp_file = config["cpp_file"]

    cpp_analyzer = CppAnalyzer()

    instance_map = {}

    for cls in all_classes:
        count = cpp_analyzer.count_instantiations(cpp_file, cls["name"])
        instance_map[cls["name"]] = count
 


    # ✅ DEBUG PARSER
    print("\n================ DEBUG PARSER ================\n")

    for header, classes in header_map.items():
        print(f"\n📄 HEADER: {header}")

        if not classes:
            print("  ❌ Keine Klassen gefunden")
            continue

        for cls in classes:
            print(f"  📦 Klasse: {cls['name']}")

            if not cls["methods"]:
                print("    ⚠️ Keine Methoden erkannt!")
                continue

            for m in cls["methods"]:
                print(f"    ✅ Methode: {m['name']}")
                print(f"       RETURN: {m['return']}")

                if not m["params"]:
                    print("       PARAMS: (keine)")
                else:
                    for ptype, pname in m["params"]:
                        print(f"       PARAM: {ptype} {pname}")

    # ✅ GENERATOR + FILE OUTPUT
    print("\n================ GENERATE FILES ================\n")

    for header, classes in header_map.items():
        print(f"\n📄 HEADER: {header}")

        for cls in classes:
            name = cls["name"]

            print(f"📦 Generiere: {name}")

            # ✅ Interface
            #iface_code = iface_gen.generate(cls)
           # iface_path = os.path.join(iface_dir, f"I{name}.h")

           # with open(iface_path, "w", encoding="utf-8") as f:
                #f.write(iface_code)

            # ✅ Fake Header
            
            count = instance_map[name]
 


            fake_code = fake_gen.generate(cls, header, count, known_types)
            fake_path = os.path.join(fake_dir, f"{name}Test.h")

            with open(fake_path, "w", encoding="utf-8") as f:
                f.write(fake_code)

            # ✅ Mock Klasse
           # mock_code = mock_gen.generate(cls)
            #mock_path = os.path.join(mock_dir, f"Mock{name}.h")

           # with open(mock_path, "w", encoding="utf-8") as f:
                #f.write(mock_code)

           # print(f"✅ Interface: {iface_path}")
            print(f"✅ Fake:      {fake_path}")
            #print(f"✅ Mock:      {mock_path}")
 
