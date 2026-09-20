# Contributing to Event Manager

Thanks for considering a contribution. This is a small Flask + SQLite app,
so the bar for changes is: keep it simple, keep it tested.

## Getting set up

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt pytest
```

## Running the tests

```bash
pytest -v
```

Every behavioral change (routes, validation, DB queries) should come with a
test in `tests/test_events.py`. Tests use `create_app(testing=True)`, which
gives each test its own throwaway SQLite file — never write tests that touch
`instance/event_manager.db`.

## Code style

- Follow the existing style: plain `sqlite3`, no ORM, app-factory pattern in
  `app/__init__.py`, view functions in `app/routes.py`.
- Keep route handlers readable: validate input, then query, then render or
  redirect. Prefer early returns over deep nesting.
- Use `flash()` for user-facing success/error messages, and keep messages
  specific enough that a real user knows what to fix.
- No new dependencies without a good reason — this project intentionally has
  a minimal `requirements.txt`.

## Submitting changes

1. Open an issue or PR describing the change and why it's useful.
2. Make sure `pytest -v` passes locally before pushing.
3. Keep commits focused — one logical change per commit, with a clear
   message describing what changed and why.
