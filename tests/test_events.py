from tests.conftest import create_event


def test_create_event(client):
    event_id = create_event(client, title="Python Conference")

    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert b"Python Conference" in response.data


def test_list_upcoming_events_shows_created_event(client):
    create_event(client, title="Future Meetup", date="2099-06-01")

    response = client.get("/events?filter=upcoming")
    assert response.status_code == 200
    assert b"Future Meetup" in response.data


def test_register_attendee_success(client):
    event_id = create_event(client, capacity=5)

    response = client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Alice", "attendee_email": "alice@example.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Alice" in response.data
    assert b"1 / 5" in response.data


def test_capacity_enforced(client):
    event_id = create_event(client, capacity=1)

    first = client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Alice", "attendee_email": "alice@example.com"},
        follow_redirects=True,
    )
    assert b"Registration successful" in first.data

    second = client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Bob", "attendee_email": "bob@example.com"},
        follow_redirects=True,
    )
    assert b"full capacity" in second.data
    assert b"Bob" not in second.data.split(b"Registered Attendees")[-1]


def test_duplicate_registration_rejected(client):
    event_id = create_event(client, capacity=5)

    client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Alice", "attendee_email": "alice@example.com"},
        follow_redirects=True,
    )
    response = client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Alice Again", "attendee_email": "ALICE@example.com"},
        follow_redirects=True,
    )
    assert b"already registered" in response.data
    detail = client.get(f"/events/{event_id}")
    assert b"1 / 5" in detail.data


def test_cancel_registration_frees_a_slot(app, client):
    event_id = create_event(client, capacity=1)

    client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Alice", "attendee_email": "alice@example.com"},
        follow_redirects=True,
    )
    detail = client.get(f"/events/{event_id}")
    assert b"FULL" in detail.data

    # Find the registration id from the DB via the app context.
    from app import get_db

    with app.app_context():
        db = get_db()
        reg = db.execute(
            "SELECT id FROM registration WHERE event_id = ?", (event_id,)
        ).fetchone()
    registration_id = reg["id"]

    cancel_response = client.post(
        f"/registrations/{registration_id}/cancel", follow_redirects=True
    )
    assert b"Registration cancelled" in cancel_response.data

    detail_after = client.get(f"/events/{event_id}")
    assert b"0 / 1" in detail_after.data
    assert b"FULL" not in detail_after.data

    second = client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Bob", "attendee_email": "bob@example.com"},
        follow_redirects=True,
    )
    assert b"Registration successful" in second.data


def test_new_event_missing_title_rejected(client):
    response = client.post(
        "/events/new",
        data={
            "title": "",
            "description": "",
            "date": "2099-01-01",
            "location": "",
            "capacity": "5",
        },
    )
    assert response.status_code == 400
    assert b"Title is required" in response.data


def test_register_with_invalid_email_rejected(client):
    event_id = create_event(client, capacity=5)

    response = client.post(
        f"/events/{event_id}/register",
        data={"attendee_name": "Alice", "attendee_email": "not-an-email"},
        follow_redirects=True,
    )
    assert b"valid email address" in response.data
    assert b"0 / 5" in response.data


def test_register_for_nonexistent_event_redirects_with_error(client):
    response = client.post(
        "/events/999999/register",
        data={"attendee_name": "Alice", "attendee_email": "alice@example.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Event not found" in response.data
