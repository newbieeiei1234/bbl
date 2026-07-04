from tests.conftest import auth_header

def _create_booking(client, header, name, detail="some detail", start="09:00", end="10:00"):
    return client.post(
        "/bookings",
        json={"name": name, "detail": detail, "start_time": start, "end_time": end},
        headers=header,
    )

def test_user_can_create_own_booking(client, normal_user):
    header = auth_header(client, *normal_user)
    resp = _create_booking(client, header, "10am-11am")
    assert resp.status_code in (200, 201), resp.text
    data = resp.json()["data"]
    assert data["name"] == "10am-11am"
    assert data["id"] is not None


def test_admin_can_create_own_booking(client, admin_user):
    header = auth_header(client, *admin_user)
    resp = _create_booking(client, header, "admin-slot")
    assert resp.status_code in (200, 201), resp.text


def test_create_booking_with_missing_fields_rejected(client, normal_user):
    header = auth_header(client, *normal_user)
    resp = client.post("/bookings", json={"name": "10am-11am"}, headers=header)
    assert resp.status_code == 422, resp.text


def test_create_booking_with_empty_name_rejected(client, normal_user):
    header = auth_header(client, *normal_user)
    resp = _create_booking(client, header, "")
    assert resp.status_code == 422, resp.text

def test_user_sees_only_their_own_bookings(client, normal_user, other_user):
    alice_header = auth_header(client, *normal_user)
    bob_header = auth_header(client, *other_user)

    _create_booking(client, alice_header, "10am-11am")
    _create_booking(client, bob_header, "2pm-3pm")

    resp = client.get("/bookings", headers=alice_header)
    assert resp.status_code == 200, resp.text
    names = [b["name"] for b in resp.json()["data"]]
    assert "10am-11am" in names
    assert "2pm-3pm" not in names, "user must not see another user's booking"


def test_user_with_no_bookings_gets_empty_list(client, normal_user):
    header = auth_header(client, *normal_user)
    resp = client.get("/bookings", headers=header)
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"] == []

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
    names = [b["name"] for b in resp.json()["data"]]
    assert "10am-11am" in names
    assert "2pm-3pm" in names

def test_user_can_edit_own_booking(client, normal_user):
    header = auth_header(client, *normal_user)
    booking = _create_booking(client, header, "10am-11am").json()["data"]

    resp = client.put(
        "/bookings",
        json={"id": booking["id"], "name": "11am-12pm", "detail": "moved"},
        headers=header,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["name"] == "11am-12pm"
    assert data["detail"] == "moved"


def test_partial_edit_keeps_other_fields(client, normal_user):
    header = auth_header(client, *normal_user)
    booking = _create_booking(
        client, header, "10am-11am", detail="original", start="10:00", end="11:00"
    ).json()["data"]

    resp = client.put(
        "/bookings", json={"id": booking["id"], "name": "renamed"}, headers=header
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["name"] == "renamed"
    assert data["detail"] == "original"
    assert data["start_time"] == "10:00"
    assert data["end_time"] == "11:00"


def test_user_cannot_edit_another_users_booking(client, normal_user, other_user):
    alice_header = auth_header(client, *normal_user)
    bob_header = auth_header(client, *other_user)
    booking = _create_booking(client, alice_header, "10am-11am").json()["data"]

    resp = client.put(
        "/bookings", json={"id": booking["id"], "name": "hijacked"}, headers=bob_header
    )
    assert resp.status_code == 403, resp.text

    names = [b["name"] for b in client.get("/bookings", headers=alice_header).json()["data"]]
    assert names == ["10am-11am"]


def test_admin_can_edit_any_users_booking(client, admin_user, normal_user):
    alice_header = auth_header(client, *normal_user)
    admin_header = auth_header(client, *admin_user)
    booking = _create_booking(client, alice_header, "10am-11am").json()["data"]

    resp = client.put(
        "/bookings", json={"id": booking["id"], "name": "admin-edit"}, headers=admin_header
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["name"] == "admin-edit"


def test_edit_nonexistent_booking_returns_404(client, normal_user):
    header = auth_header(client, *normal_user)
    resp = client.put("/bookings", json={"id": 99999, "name": "ghost"}, headers=header)
    assert resp.status_code == 404, resp.text

def test_booking_endpoints_require_authentication(client):
    assert client.get("/bookings").status_code == 401
    assert client.get("/bookings/all").status_code == 401
    assert client.post(
        "/bookings",
        json={"name": "9am", "detail": "d", "start_time": "09:00", "end_time": "10:00"},
    ).status_code == 401
    assert client.put("/bookings", json={"id": 1, "name": "x"}).status_code == 401


def test_booking_endpoints_reject_invalid_token(client):
    header = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/bookings", headers=header).status_code == 401
    assert client.get("/bookings/all", headers=header).status_code == 401
