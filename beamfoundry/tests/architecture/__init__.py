# tests/architecture/__init__.py
"""
Architecture Test Suite

This package contains tests that enforce *structural invariants* of the
application. These tests are not concerned with functional behavior or
business logic. Instead, they protect the integrity of the application's
architecture:

- Blueprint identity must be stable and unique.
- Blueprints must register routes.
- No module may raise at import time.
- Diagnostics routes must always exist.
- No blueprint may be redefined inside a routes module.
- No module may be imported under multiple identities.

Architecture tests act as a structural firewall. They prevent entire classes
of regressions that normal unit tests cannot detect.

See manifest.md for detailed guidance on extending this suite.
"""
