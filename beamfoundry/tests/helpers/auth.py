# filename: tests/helpers/auth.py


def authenticate(client):
    """
    Inject a logged-in session for tests that hit login-gated routes.
    """
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True
