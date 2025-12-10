# logexp/app/blueprints/__init__.py
from importlib import import_module

def register_blueprints(app):
    """
    Dynamically import and register all blueprints.
    Each blueprint file must expose `bp` as its Blueprint instance.
    """
    blueprint_modules = [
        "logexp.app.routes",       # main UI/navigation
        "logexp.app.readings",     # readings API
        "logexp.app.diagnostics",  # diagnostics endpoints
        "logexp.app.docs",         # docs page
        "logexp.app.about",        # about page
    ]

    for module_path in blueprint_modules:
        module = import_module(module_path)
        app.register_blueprint(module.bp)
