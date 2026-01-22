# filename: tests/architecture/test_blueprint_import_count.py

"""
Ensures each blueprint package imports cleanly and appears exactly once in
sys.modules after import. This catches shadow imports caused by inconsistent
import paths.
"""

import importlib
import sys

BLUEPRINT_PACKAGES = [
    "app.bp.ui",
    "app.bp.api",
    "app.bp.settings",
    "app.bp.diagnostics",
    "app.bp.analytics",
    "app.bp.docs",
    "app.bp.about",
]


def test_blueprint_imports_are_unique():
    for pkg in BLUEPRINT_PACKAGES:
        # Force import
        importlib.import_module(pkg)

        # Collect all module identities that match this package exactly
        matches = [name for name in sys.modules if name == pkg]

        assert matches, f"Blueprint package '{pkg}' did not import into sys.modules"

        assert len(matches) == 1, f"Blueprint package '{pkg}' imported multiple times: {matches}"
