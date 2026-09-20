"""Seed the local development database with realistic sample data.

This is useful when you want to demo the app or manually poke around the UI
without clicking through "New Event" and the registration form by hand.

Usage:

    python3 examples/seed_sample_data.py

It creates the app's normal instance database (the same one `python app.py`
uses), adds a few events with different capacities and dates, and registers
a handful of attendees so you can immediately see a "full" event, an event
with open spots, and a past event in the "past" filter.

Run it once, then `python app.py` and visit http://127.0.0.1:5000/events.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, get_db  # noqa: E402


def seed():
    app = create_app()

    with app.app_context():
        db = get_db()

        events = [
            ("PyData Meetup", "Monthly talks on data tooling.", "2099-03-15", "Community Hall", 3),
            ("Board Game Night", "Bring a game or learn a new one.", "2099-04-02", "The Attic", 10),
            ("Retro Arcade Expo", "Wrapped up last month.", "2020-01-10", "Convention Center", 50),
        ]

        event_ids = []
        for title, description, date, location, capacity in events:
            existing = db.execute(
                "SELECT id FROM event WHERE title = ?", (title,)
            ).fetchone()
            if existing:
                event_ids.append(existing["id"])
                continue
            cur = db.execute(
                "INSERT INTO event (title, description, date, location, capacity) "
                "VALUES (?, ?, ?, ?, ?)",
                (title, description, date, location, capacity),
            )
            db.commit()
            event_ids.append(cur.lastrowid)

        pydata_id = event_ids[0]
        attendees = [
            ("Alice Chen", "alice@example.com"),
            ("Bob Kumar", "bob@example.com"),
            ("Cy Osei", "cy@example.com"),
        ]
        for name, email in attendees:
            already = db.execute(
                "SELECT id FROM registration WHERE event_id = ? AND attendee_email = ?",
                (pydata_id, email),
            ).fetchone()
            if already:
                continue
            db.execute(
                "INSERT INTO registration (event_id, attendee_name, attendee_email, registered_at) "
                "VALUES (?, ?, ?, ?)",
                (pydata_id, name, email, datetime.now().isoformat(timespec="seconds")),
            )
        db.commit()

    print("Seeded sample events and registrations into the app's instance database.")
    print("PyData Meetup is now at capacity (3/3) to demonstrate the full-event message.")


if __name__ == "__main__":
    seed()
