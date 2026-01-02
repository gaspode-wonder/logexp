def test_all_blueprints_register_routes(test_app):
    rules = list(test_app.url_map.iter_rules())
    endpoints = {rule.endpoint for rule in rules}

    expected = {
        "ui",
        "api",
        "settings",
        "diagnostics",
        "analytics",
        "docs",
        "about",
    }

    for bp in expected:
        assert any(ep.startswith(f"{bp}.") for ep in endpoints), (
            f"Blueprint '{bp}' registered with ZERO routes — "
            "likely import-time failure or duplicate module identity."
        )
