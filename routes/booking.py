from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import database
from routes.utils import login_required, log_activity

booking_bp = Blueprint("booking", __name__, template_folder="../templates/booking", url_prefix="/booking")


@booking_bp.route("/")
@login_required
def index():
    db = database.get_db()
    bookings = db.execute("""
        SELECT bookings.*, assets.name AS resource_name, users.name AS booked_by_name
        FROM bookings
        JOIN assets ON assets.id = bookings.resource_asset_id
        JOIN users ON users.id = bookings.booked_by
        ORDER BY start_time
    """).fetchall()
    return render_template("booking/index.html", bookings=bookings)


@booking_bp.route("/book", methods=["GET", "POST"])
@login_required
def book():
    db = database.get_db()

    if request.method == "POST":
        resource_id = request.form["resource_asset_id"]
        start_time = request.form["start_time"]   # 'YYYY-MM-DD HH:MM'
        end_time = request.form["end_time"]

        # --- THE CORE OVERLAP RULE ---
        # Two ranges overlap unless one ends at/before the other starts.
        # New booking conflicts with an existing one iff:
        #   new_start < existing_end  AND  new_end > existing_start
        # This correctly ALLOWS back-to-back bookings (e.g. new booking
        # starting exactly when the previous one ends).
        conflict = db.execute("""
            SELECT id FROM bookings
            WHERE resource_asset_id = ?
              AND status IN ('upcoming', 'ongoing')
              AND ? < end_time AND ? > start_time
        """, (resource_id, start_time, end_time)).fetchone()

        if conflict:
            flash("This slot overlaps with an existing booking for this resource. Choose a different time.")
            return redirect(url_for("booking.book"))

        db.execute(
            "INSERT INTO bookings (resource_asset_id, booked_by, start_time, end_time, status) "
            "VALUES (?, ?, ?, ?, 'upcoming')",
            (resource_id, session["user_id"], start_time, end_time),
        )
        db.commit()
        log_activity(session["user_id"], "booked resource", f"resource_id={resource_id}")
        flash("Booking confirmed.")
        return redirect(url_for("booking.index"))

    resources = db.execute("SELECT * FROM assets WHERE is_bookable = 1").fetchall()
    return render_template("booking/book.html", resources=resources)


@booking_bp.route("/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel(booking_id):
    db = database.get_db()
    db.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    db.commit()
    log_activity(session["user_id"], "cancelled booking", f"booking_id={booking_id}")
    return redirect(url_for("booking.index"))
