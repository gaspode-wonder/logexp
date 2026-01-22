# tests/test_blueprint_registration.py


def test_all_blueprints_register_routes(test_app):
    rules = list(test_app.url_map.iter_rules())
    endpoints = {rule.endpoint for rule in rules}

    # These are the blueprints we expect to have at least one endpoint
    expected_blueprints = {
        "ui",
        "api",
        "settings",
        "diagnostics",
        "analytics",
        "docs",
        "about",
    }

    for bp in expected_blueprints:
        assert any(
            ep.startswith(f"{bp}.") for ep in endpoints
        ), f"Blueprint '{bp}' registered with ZERO routes — likely import-time failure"
