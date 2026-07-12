from flask import Blueprint, render_template, request, redirect, url_for, session
import database
from routes.utils import login_required, role_required, log_activity

assets_bp = Blueprint("assets", __name__, template_folder="../templates/assets", url_prefix="/assets")


@assets_bp.route("/")
@login_required
def index():
    db = database.get_db()
    q = request.args.get("q", "")
    assets = db.execute(
        "SELECT * FROM assets WHERE asset_tag LIKE ? OR name LIKE ? ORDER BY id DESC",
        (f"%{q}%", f"%{q}%"),
    ).fetchall()
    return render_template("assets/index.html", assets=assets, q=q)


@assets_bp.route("/new", methods=["GET", "POST"])
@role_required("asset_manager", "admin")
def new():
    db = database.get_db()
    if request.method == "POST":
        # Auto-generate the next asset tag, e.g. AF-0001, AF-0002, ...
        last = db.execute("SELECT asset_tag FROM assets ORDER BY id DESC LIMIT 1").fetchone()
        next_num = int(last["asset_tag"].split("-")[1]) + 1 if last else 1
        asset_tag = f"AF-{next_num:04d}"

        db.execute("""INSERT INTO assets
            (asset_tag, name, category_id, serial_number, location, condition,
             is_bookable, acquisition_cost, acquisition_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (asset_tag, request.form["name"], request.form.get("category_id") or None,
             request.form.get("serial_number"), request.form.get("location"),
             request.form.get("condition"), 1 if request.form.get("is_bookable") else 0,
             request.form.get("acquisition_cost") or None, request.form.get("acquisition_date")))
        db.commit()
        log_activity(session["user_id"], "registered asset", asset_tag)
        return redirect(url_for("assets.index"))

    categories = db.execute("SELECT * FROM asset_categories").fetchall()
    return render_template("assets/new.html", categories=categories)


@assets_bp.route("/<int:asset_id>")
@login_required
def detail(asset_id):
    db = database.get_db()
    asset = db.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    allocations = db.execute(
        """SELECT allocations.*, users.name AS employee_name FROM allocations
           JOIN users ON users.id = allocations.employee_id
           WHERE asset_id = ? ORDER BY allocated_on DESC""", (asset_id,)
    ).fetchall()
    maintenance = db.execute(
        "SELECT * FROM maintenance_requests WHERE asset_id = ? ORDER BY id DESC", (asset_id,)
    ).fetchall()
    return render_template("assets/detail.html", asset=asset, allocations=allocations, maintenance=maintenance)
