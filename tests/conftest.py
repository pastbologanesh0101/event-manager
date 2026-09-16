import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app import create_app


@pytest.fixture
def app():
    flask_app = create_app(testing=True)
    db_path = flask_app.config["DATABASE"]
    yield flask_app
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def create_event(client, title="Test Event", date="2099-01-01", capacity=2,
                  description="A test event", location="Test Hall"):
    """Create an event and return its new event_id (parsed from the redirect)."""
    response = client.post(
        "/events/new",
        data={
            "title": title,
            "description": description,
            "date": date,
            "location": location,
            "capacity": str(capacity),
        },
    )
    assert response.status_code == 302
    location = response.headers["Location"]
    return int(location.rstrip("/").rsplit("/", 1)[-1])
