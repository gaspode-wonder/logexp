import ast
from pathlib import Path


def test_no_blueprint_redefinition():
    routes_path = Path("logexp/app/bp/diagnostics/routes.py")
    tree = ast.parse(routes_path.read_text())

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(
                isinstance(t, ast.Name) and t.id == "bp_diagnostics"
                for t in node.targets
            ):
                raise AssertionError(
                    "bp_diagnostics is redefined in routes.py — "
                    "blueprint must be defined only in __init__.py"
                )
