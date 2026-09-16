from datetime import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from . import get_db

bp = Blueprint("events", __name__)


def _today_str():
    return datetime.now().strftime("%Y-%m-%d")


@bp.route("/")
def index():
    return redirect(url_for("events.list_events"))


@bp.route("/events")
def list_events():
    db = get_db()
    filt = request.args.get("filter", "upcoming")
    today = _today_str()

    if filt == "past":
        rows = db.execute(
            "SELECT * FROM event WHERE date < ? ORDER BY date DESC", (today,)
        ).fetchall()
    else:
        filt = "upcoming"
        rows = db.execute(
            "SELECT * FROM event WHERE date >= ? ORDER BY date ASC", (today,)
        ).fetchall()

    events = []
    for row in rows:
        count = db.execute(
            "SELECT COUNT(*) AS c FROM registration WHERE event_id = ?", (row["id"],)
        ).fetchone()["c"]
        events.append({**dict(row), "registration_count": count})

    return render_template("events/list.html", events=events, filter=filt)


@bp.route("/events/new", methods=["GET", "POST"])
def new_event():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        date = request.form.get("date", "").strip()
        location = request.form.get("location", "").strip()
        capacity = request.form.get("capacity", "").strip()

        errors = []
        if not title:
            errors.append("Title is required.")
        if not date:
            errors.append("Date is required.")
        else:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                errors.append("Date must be in YYYY-MM-DD format.")
        try:
            capacity_int = int(capacity)
            if capacity_int <= 0:
                errors.append("Capacity must be a positive integer.")
        except (TypeError, ValueError):
            errors.append("Capacity must be a positive integer.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("events/new.html", form=request.form), 400

        db = get_db()
        cur = db.execute(
            "INSERT INTO event (title, description, date, location, capacity) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, description, date, location, capacity_int),
        )
        db.commit()
        flash("Event created successfully.", "success")
        return redirect(url_for("events.event_detail", event_id=cur.lastrowid))

    return render_template("events/new.html", form={})


@bp.route("/events/<int:event_id>")
def event_detail(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM event WHERE id = ?", (event_id,)).fetchone()
    if event is None:
        flash("Event not found.", "error")
        return redirect(url_for("events.list_events"))

    registrations = db.execute(
        "SELECT * FROM registration WHERE event_id = ? ORDER BY registered_at ASC",
        (event_id,),
    ).fetchall()

    return render_template(
        "events/detail.html",
        event=event,
        registrations=registrations,
        registration_count=len(registrations),
        spots_left=event["capacity"] - len(registrations),
    )


@bp.route("/events/<int:event_id>/register", methods=["POST"])
def register(event_id):
    db = get_db()
    event = db.execute("SELECT * FROM event WHERE id = ?", (event_id,)).fetchone()
    if event is None:
        flash("Event not found.", "error")
        return redirect(url_for("events.list_events"))

    name = request.form.get("attendee_name", "").strip()
    email = request.form.get("attendee_email", "").strip().lower()

    if not name or not email:
        flash("Name and email are required to register.", "error")
        return redirect(url_for("events.event_detail", event_id=event_id))

    current_count = db.execute(
        "SELECT COUNT(*) AS c FROM registration WHERE event_id = ?", (event_id,)
    ).fetchone()["c"]

    if current_count >= event["capacity"]:
        flash("This event is at full capacity.", "error")
        return redirect(url_for("events.event_detail", event_id=event_id))

    existing = db.execute(
        "SELECT id FROM registration WHERE event_id = ? AND attendee_email = ?",
        (event_id, email),
    ).fetchone()
    if existing is not None:
        flash("This email is already registered for this event.", "error")
        return redirect(url_for("events.event_detail", event_id=event_id))

    db.execute(
        "INSERT INTO registration (event_id, attendee_name, attendee_email, registered_at) "
        "VALUES (?, ?, ?, ?)",
        (event_id, name, email, datetime.now().isoformat(timespec="seconds")),
    )
    db.commit()
    flash("Registration successful.", "success")
    return redirect(url_for("events.event_detail", event_id=event_id))


@bp.route("/registrations/<int:registration_id>/cancel", methods=["POST"])
def cancel_registration(registration_id):
    db = get_db()
    reg = db.execute(
        "SELECT * FROM registration WHERE id = ?", (registration_id,)
    ).fetchone()
    if reg is None:
        flash("Registration not found.", "error")
        return redirect(url_for("events.list_events"))

    event_id = reg["event_id"]
    db.execute("DELETE FROM registration WHERE id = ?", (registration_id,))
    db.commit()
    flash("Registration cancelled.", "success")
    return redirect(url_for("events.event_detail", event_id=event_id))
