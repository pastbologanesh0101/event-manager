# Event Manager

A small Flask + SQLite event management system. Create events, let attendees
register with capacity limits, and manage registrations — all server-rendered
with Jinja2 templates and plain CSS, no JavaScript framework required.

## Features

- Create events with a title, description, date, location, and capacity.
- Browse upcoming and past events.
- View an event's detail page with a live registration count and remaining
  spots.
- Register for an event with a name and email — registration is rejected if
  the event is at full capacity or the email has already registered for that
  event.
- Cancel a registration to free up a slot.

## Tech stack

- **Flask** (app factory pattern via `create_app()`)
- **SQLite** (accessed with the standard library `sqlite3` module, no ORM)
- **Jinja2** server-rendered templates
- Plain CSS (no build step, no frontend framework)

## Project structure

```
event-manager/
├── app/
│   ├── __init__.py       # app factory, DB setup/teardown
│   ├── routes.py         # all view functions (blueprint)
│   ├── templates/        # Jinja2 templates
│   └── static/style.css  # plain CSS
├── tests/
│   ├── conftest.py       # pytest fixtures + test helpers
│   └── test_events.py    # unit tests using Flask's test client
├── app.py                # entry point (flask run / python app.py)
├── requirements.txt
└── .github/workflows/tests.yml
```

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python app.py
# or: flask --app app run
```

The app will be available at `http://127.0.0.1:5000/`. On first run it
creates a SQLite database at `instance/event_manager.db` (ignored by git).

## Running the tests

```bash
pip install -r requirements.txt pytest
pytest -v
```

Tests use `create_app(testing=True)`, which points the app at an isolated,
throwaway SQLite database file per test so they never touch your real data.

## Example usage

1. Go to **New Event**, fill in a title, date (`YYYY-MM-DD`), location, and
   capacity (e.g. capacity `2`), and submit.
2. On the event detail page, register an attendee with a name and email.
3. Try registering the same email again — it will be rejected as a duplicate.
4. Fill the event to capacity — a further registration attempt will be
   rejected with a "full capacity" message.
5. Cancel a registration from the detail page to free up a slot, then
   register a new attendee into that freed slot.

## Troubleshooting / FAQ

**I ran `python app.py` twice and my old events disappeared.**
`init_db()` only creates tables with `CREATE TABLE IF NOT EXISTS`, so it
never drops data. If events look missing, check that you're running from
the same working directory each time — `instance/event_manager.db` is a
relative path, so running the app from a different folder creates (or
reads) a different database file.

**Registering with a valid-looking email still gets rejected.**
The app does a lightweight format check (must contain `@` and a `.` in the
domain part) rather than a full RFC 5322 validation. Addresses like
`user@localhost` (no dot) will be rejected even though some mail servers
accept them. This is intentional for a small internal tool — swap in a
proper validator (e.g. `email-validator`) if you need stricter or looser
rules.

**Why do dates have to be `YYYY-MM-DD`?**
Event dates are stored as plain `TEXT` in SQLite and compared with string
comparison (`WHERE date >= ?`) to split upcoming vs. past events. That only
sorts correctly if every date uses the same zero-padded `YYYY-MM-DD` format,
so the form rejects anything else rather than risk silently mis-sorting
events.

**The capacity count on the detail page seems off after cancelling.**
Registration counts are computed live with `COUNT(*)` on every page load
(there's no cached counter column), so the number always reflects the
current `registration` table. If it looks stale, it's almost always a
browser cache — hard refresh the page.

## License

MIT — see [LICENSE](LICENSE).
