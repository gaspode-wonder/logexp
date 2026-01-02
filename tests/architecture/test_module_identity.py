# filename: tests/architecture/test_module_identity.py

import sys


def test_no_duplicate_module_identities():
    # Find all module identities for the diagnostics *package* (not submodules)
    diagnostics_packages = [
        name for name in sys.modules if name.endswith("bp.diagnostics")
    ]

    # If diagnostics hasn't been imported yet, that's fine.
    if not diagnostics_packages:
        return

    # Otherwise, enforce the invariant.
    assert len(diagnostics_packages) == 1, (
        f"Diagnostics package imported under multiple identities: "
        f"{diagnostics_packages}"
    )
