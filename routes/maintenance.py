from flask import Blueprint, render_template, request, redirect, url_for, session
import database
from routes.utils import login_required, role_required, log_activity

maintenance_bp = Blueprint("maintenance", __name__, template_folder="../templates/maintenance", url_prefix="/maintenance")


@maintenance_bp.route("/")
@login_required
def index():
    db = database.get_db()
    requests_ = db.execute("""
        SELECT maintenance_requests.*, assets.name AS asset_name, assets.asset_tag
        FROM maintenance_requests JOIN assets ON assets.id = maintenance_requests.asset_id
        ORDER BY maintenance_requests.id DESC
    """).fetchall()
    return render_template("maintenance/index.html", requests=requests_)


@maintenance_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    db = database.get_db()
    if request.method == "POST":
        asset_id = request.form["asset_id"]
        issue = request.form["issue"]
        priority = request.form["priority"]
        db.execute(
            "INSERT INTO maintenance_requests (asset_id, raised_by, issue, priority) VALUES (?, ?, ?, ?)",
            (asset_id, session["user_id"], issue, priority),
        )
        db.commit()
        log_activity(session["user_id"], "raised maintenance request", f"asset_id={asset_id}")
        return redirect(url_for("maintenance.index"))
    assets = db.execute("SELECT * FROM assets").fetchall()
    return render_template("maintenance/new.html", assets=assets)


@maintenance_bp.route("/<int:req_id>/approve", methods=["POST"])
@role_required("asset_manager", "admin")
def approve(req_id):
    db = database.get_db()
    req = db.execute("SELECT * FROM maintenance_requests WHERE id = ?", (req_id,)).fetchone()
    db.execute("UPDATE maintenance_requests SET status = 'approved' WHERE id = ?", (req_id,))
    db.execute("UPDATE assets SET status = 'maintenance' WHERE id = ?", (req["asset_id"],))
    db.commit()
    log_activity(session["user_id"], "approved maintenance request", f"req_id={req_id}")
    return redirect(url_for("maintenance.index"))


@maintenance_bp.route("/<int:req_id>/reject", methods=["POST"])
@role_required("asset_manager", "admin")
def reject(req_id):
    db = database.get_db()
    db.execute("UPDATE maintenance_requests SET status = 'rejected' WHERE id = ?", (req_id,))
    db.commit()
    log_activity(session["user_id"], "rejected maintenance request", f"req_id={req_id}")
    return redirect(url_for("maintenance.index"))


@maintenance_bp.route("/<int:req_id>/resolve", methods=["POST"])
@role_required("asset_manager", "admin")
def resolve(req_id):
    db = database.get_db()
    req = db.execute("SELECT * FROM maintenance_requests WHERE id = ?", (req_id,)).fetchone()
    db.execute("UPDATE maintenance_requests SET status = 'resolved' WHERE id = ?", (req_id,))
    db.execute("UPDATE assets SET status = 'available' WHERE id = ?", (req["asset_id"],))
    db.commit()
    log_activity(session["user_id"], "resolved maintenance request", f"req_id={req_id}")
    return redirect(url_for("maintenance.index"))
