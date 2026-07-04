from tests.conftest import register_user, login, auth_token

def test_register_new_user_succeeds(client):
    resp = register_user(client, "newuser", "secret123", admin=False)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["username"] == "newuser"
    assert "secret123" not in resp.text


def test_register_duplicate_username_rejected(client):
    assert register_user(client, "dupe", "pw1").status_code == 200
    resp = register_user(client, "dupe", "pw2")
    assert resp.status_code >= 400
    assert "exist" in resp.text.lower()

def test_login_with_valid_credentials_returns_token(client, normal_user):
    username, password = normal_user
    resp = login(client, username, password)
    assert resp.status_code == 200, resp.text
    token = auth_token(resp)
    assert token, "login should return a non-empty access token"


def test_login_with_wrong_password_is_unauthorized(client, normal_user):
    username, _ = normal_user
    resp = login(client, username, "wrong-password")
    assert resp.status_code in (400, 401), resp.text
    assert auth_token(resp) is None


def test_login_with_unknown_user_is_rejected(client):
    resp = login(client, "ghost", "whatever")
    assert resp.status_code in (401, 404), resp.text
    assert auth_token(resp) is None


def test_admin_can_login(client, admin_user):
    username, password = admin_user
    resp = login(client, username, password)
    assert resp.status_code == 200, resp.text
    assert auth_token(resp)
