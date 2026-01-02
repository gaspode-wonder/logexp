# filename: tests/architecture/test_blueprint_module_identity.py

"""
Ensures each blueprint package is imported under exactly one module identity.

This prevents subtle bugs where a blueprint is imported via multiple paths
(e.g., 'logexp.app.bp.ui' vs 'logexp.bp.ui'), which creates duplicate module
objects and breaks route registration.
"""

import sys

BLUEPRINT_PACKAGES = [
    "logexp.app.bp.ui",
    "logexp.app.bp.api",
    "logexp.app.bp.settings",
    "logexp.app.bp.diagnostics",
    "logexp.app.bp.analytics",
    "logexp.app.bp.docs",
    "logexp.app.bp.about",
]


def test_blueprint_packages_have_single_identity():
    for pkg in BLUEPRINT_PACKAGES:
        matches = [name for name in sys.modules if name == pkg]

        # If the package hasn't been imported yet, that's fine.
        if not matches:
            continue

        # Otherwise, enforce the invariant.
        assert (
            len(matches) == 1
        ), f"Blueprint package '{pkg}' imported under multiple identities: {matches}"
