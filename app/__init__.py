import os
import sqlite3
from datetime import datetime

from flask import Flask, current_app, g


def get_db():
    """Return a request-scoped SQLite connection stored on flask.g."""
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def init_db(app):
    """Create tables if they do not already exist."""
    db_path = app.config["DATABASE"]
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            date TEXT NOT NULL,
            location TEXT NOT NULL DEFAULT '',
            capacity INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            attendee_name TEXT NOT NULL,
            attendee_email TEXT NOT NULL,
            registered_at TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES event (id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


def create_app(testing=False, database=None):
    """Application factory.

    When ``testing`` is True (or ``database`` is given) the app uses an
    isolated SQLite database file so tests never touch real data.
    """
    app = Flask(__name__, instance_relative_config=True)

    if database is not None:
        db_path = database
    elif testing:
        # Each test app gets its own throwaway file-based sqlite DB so that
        # multiple connections within the same test see the same data
        # (a pure in-memory DB is per-connection, which breaks Flask's
        # per-request connection model).
        import tempfile

        fd, db_path = tempfile.mkstemp(prefix="event_manager_test_", suffix=".db")
        os.close(fd)
    else:
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, "event_manager.db")

    app.config.update(
        TESTING=testing,
        DATABASE=db_path,
        SECRET_KEY="dev-secret-key-change-in-production",
    )

    init_db(app)

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    from . import routes

    app.register_blueprint(routes.bp)

    @app.template_filter("format_date")
    def format_date(value):
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            return value

    return app
