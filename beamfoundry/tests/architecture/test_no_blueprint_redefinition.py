# filename: tests/architecture/test_no_blueprint_redefinition.py

"""
Ensures no blueprint is redefined inside any routes.py file.

Blueprints must be defined in the package __init__.py and imported into
routes.py. Redefining a Blueprint inside routes.py creates a second blueprint
object, causing routes to attach to the wrong instance.
"""

import ast
from pathlib import Path

BLUEPRINT_DIR = Path("logexp/app/bp")


def test_no_blueprint_redefinition_in_routes():
    for routes_file in BLUEPRINT_DIR.rglob("routes.py"):
        tree = ast.parse(routes_file.read_text())

        for node in ast.walk(tree):
            # Detect Blueprint(...) calls
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Blueprint":
                raise AssertionError(
                    f"Blueprint() call found in {routes_file}. "
                    "Blueprints must be defined only in __init__.py."
                )

            # Detect assignments like bp_ui = ..., bp_api = ..., etc.
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith("bp_"):
                        raise AssertionError(
                            f"Blueprint variable '{target.id}' assigned in {routes_file}. "
                            "Blueprints must not be defined in routes.py."
                        )
