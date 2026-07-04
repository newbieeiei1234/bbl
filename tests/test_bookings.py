from tests.conftest import auth_header, register_user


def _create_booking(client, header, slot):
    return client.post("/bookings", json={"name": slot}, headers=header)

def test_user_can_create_own_booking(client, normal_user):
    header = auth_header(client, *normal_user)
    resp = _create_booking(client, header, "10am-11am")
    assert resp.status_code in (200, 201), resp.text


def test_user_sees_only_their_own_bookings(client, normal_user, other_user):
    alice_header = auth_header(client, *normal_user)
    bob_header = auth_header(client, *other_user)

    _create_booking(client, alice_header, "10am-11am")
    _create_booking(client, bob_header, "2pm-3pm")

    resp = client.get("/bookings", headers=alice_header)
    assert resp.status_code == 200, resp.text
    slots = resp.text
    assert "10am-11am" in slots
    assert "2pm-3pm" not in slots, "user must not see another user's booking"


def test_non_admin_cannot_view_all_bookings(client, normal_user):
    header = auth_header(client, *normal_user)
    resp = client.get("/bookings/all", headers=header)
    assert resp.status_code in (401, 403), resp.text

def test_admin_can_view_all_bookings(client, admin_user, normal_user, other_user):
    alice_header = auth_header(client, *normal_user)
    bob_header = auth_header(client, *other_user)
    _create_booking(client, alice_header, "10am-11am")
    _create_booking(client, bob_header, "2pm-3pm")

    admin_header = auth_header(client, *admin_user)
    resp = client.get("/bookings/all", headers=admin_header)
    assert resp.status_code == 200, resp.text
    body = resp.text
    assert "10am-11am" in body
    assert "2pm-3pm" in body

def test_booking_endpoints_require_authentication(client):
    assert client.get("/bookings").status_code == 401
    assert client.get("/bookings/all").status_code == 401
    assert client.post("/bookings", json={"name": "9am-10am"}).status_code == 401
