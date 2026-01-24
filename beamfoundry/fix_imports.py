#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).parent
APP_DIR = ROOT / "app"

# Only match imports that start with "from app." or "import app."
PATTERNS = [
    (
        re.compile(r"^(\s*)from\s+app(\.[\w\.]+)\s+import\s+"),
        r"\1from .\2 import ",
    ),
    (
        re.compile(r"^(\s*)import\s+app(\.[\w\.]+)"),
        r"\1from . import \2",
    ),
]


def rewrite_imports(path: Path, write: bool) -> None:
    original = path.read_text().splitlines()
    rewritten = []
    changed = False

    for line in original:
        new_line = line

        # Only rewrite if the line starts with "from app" or "import app"
        if new_line.lstrip().startswith(("from app.", "import app.")):
            for pattern, repl in PATTERNS:
                if pattern.match(new_line):
                    new_line = pattern.sub(repl, new_line)
                    changed = True

        rewritten.append(new_line)

    if changed:
        if write:
            path.write_text("\n".join(rewritten) + "\n")
            print(f"[UPDATED] {path}")
        else:
            print(f"[DRY RUN] Would update: {path}")
    else:
        print(f"[OK]      {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix absolute imports inside app/ package.")
    parser.add_argument("--write", action="store_true", help="Apply changes instead of dry-run.")
    args = parser.parse_args()

    print(f"Scanning {APP_DIR} ...")
    for pyfile in APP_DIR.rglob("*.py"):
        rewrite_imports(pyfile, args.write)

    if not args.write:
        print("\nDry run complete. Use --write to apply changes.")


if __name__ == "__main__":
    main()
