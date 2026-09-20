# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2025-09-17

Initial release.

### Added

- Flask application factory (`create_app()`) with SQLite storage via the
  standard library `sqlite3` module — no ORM.
- Event model: title, description, date, location, and capacity, with
  auto-created tables on startup.
- Registration model: attendee name and email tied to an event via a
  foreign key with `ON DELETE CASCADE`.
- Routes for creating events, listing upcoming/past events, viewing an
  event's detail page, registering an attendee, and cancelling a
  registration.
- Server-side validation on event creation: required title, `YYYY-MM-DD`
  date format, and positive integer capacity.
- Registration guards: rejects registrations once an event is at full
  capacity, and rejects duplicate registrations from the same email
  (case-insensitive) for the same event.
- Server-rendered Jinja2 templates and plain CSS (no frontend framework).
- Test suite using Flask's test client against an isolated per-test SQLite
  database (`tests/test_events.py`, `tests/conftest.py`).
- GitHub Actions CI running the test suite on Python 3.11 and 3.12.
- MIT license.
