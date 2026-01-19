import importlib
import pkgutil

import app.services as services


def test_service_modules_import_cleanly():
    for module in pkgutil.walk_packages(services.__path__, services.__name__ + "."):
        name = module.name
        try:
            importlib.import_module(name)
        except Exception as exc:
            raise AssertionError(f"Import-time failure in service module '{name}': {exc}") from exc
