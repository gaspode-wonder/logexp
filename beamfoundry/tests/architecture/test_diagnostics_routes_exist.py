def test_diagnostics_routes_exist(test_app):
    endpoints = {rule.endpoint for rule in test_app.url_map.iter_rules()}

    assert "diagnostics.diagnostics_index" in endpoints
    assert "diagnostics.diagnostics_test" in endpoints
    assert any(ep.startswith("diagnostics.diagnostics_page") for ep in endpoints)
