# filename: scripts/ci_diagnostics.py

import importlib
import os
import sys


def print_header(title: str) -> None:
    print(f"\n### {title}")


def main() -> None:
    print_header("Working Directory")
    print(os.getcwd())

    print_header("Directory Tree")
    for root, dirs, files in os.walk(".", topdown=True):
        level = root.count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

    print_header("Python sys.path")
    for p in sys.path:
        print("  ", p)

    print_header("Filtered Environment Variables")
    for k in sorted(os.environ):
        if any(x in k for x in ["SQL", "FLASK", "PYTHON", "TZ", "ANALYTICS"]):
            print(f"{k}={os.environ[k]}")

    print_header("Import Resolution Test")

    def try_import(name: str) -> None:
        try:
            mod = importlib.import_module(name)
            print(f"Imported {name}: {getattr(mod, '__file__', 'built-in')}")
        except Exception as e:
            print(f"FAILED to import {name}: {e}")

    try_import("beamfoundry")
    try_import("beamfoundry.app")

    print_header("Python Executable")
    print(sys.executable)

    print_header("Current Working Directory (Python)")
    print(os.getcwd())


if __name__ == "__main__":
    main()
