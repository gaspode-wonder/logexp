import app.bp.diagnostics as pkg
import app.bp.diagnostics.routes as routes


def test_diagnostics_blueprint_is_singleton():
    assert pkg.bp_diagnostics is routes.bp_diagnostics, (
        "Diagnostics blueprint imported under two identities — " "this causes silent route loss."
    )
