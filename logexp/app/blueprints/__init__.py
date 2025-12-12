from importlib import import_module

def register_blueprints(app):
    """
    Dynamically import and register all blueprints.
    Each blueprint file must expose one or more Blueprint instances.
    """
    blueprint_modules = [
        "logexp.app.routes",       # main UI/navigation
        "logexp.app.readings",     # readings UI + API
        "logexp.app.diagnostics",  # diagnostics endpoints
        "logexp.app.docs",         # docs page
        "logexp.app.about",        # about page
    ]

    for module_path in blueprint_modules:
        module = import_module(module_path)
        # register all Blueprint objects defined in the module
        for attr in dir(module):
            obj = getattr(module, attr)
            if hasattr(obj, "register") and getattr(obj, "name", None):
                app.register_blueprint(obj)
