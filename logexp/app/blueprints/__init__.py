from importlib import import_module
from flask import Blueprint

def register_blueprints(app):
    """
    Import and register all blueprints.
    Each blueprint file must expose one or more Blueprint instances.
    """
    blueprint_modules = [
        "logexp.app.routes",
        "logexp.app.readings",
        "logexp.app.diagnostics",
        "logexp.app.docs",
        "logexp.app.about",
    ]

    for module_path in blueprint_modules:
        module = import_module(module_path)
        # Only register attributes that are actually Flask Blueprints
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, Blueprint):
                app.register_blueprint(obj)
