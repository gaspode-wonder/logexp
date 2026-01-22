# filename: beamfoundry/scripts/preflight.py
#!/usr/bin/env python3
import os
import platform
import sys

print("=== Beamfoundry Local Preflight ===")
print("CWD:", os.getcwd())
print("Python:", sys.executable)
print("Version:", sys.version)
print("Platform:", platform.platform())

print("\nFiltered ENV:")
for k, v in os.environ.items():
    if any(x in k for x in ["SQL", "FLASK", "PYTHON", "TZ", "ANALYTICS"]):
        print(f"  {k}={v}")

print("\nImport Test:")
try:
    import app
    print("app package:", app.__file__)

    import beamfoundry_app
    print("beamfoundry_app:", beamfoundry_app.__file__)

except Exception as e:
    print("Import error:", e)

print("\n=== Preflight Complete ===")
