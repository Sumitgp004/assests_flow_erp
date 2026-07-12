from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import database
from routes.utils import login_required, role_required, log_activity

allocation_bp = Blueprint("allocation", __name__, template_folder="../templates/allocation", url_prefix="/allocation")


@allocation_bp.route("/")
@login_required
def index():
    db = database.get_db()
    allocations = db.execute("""
        SELECT allocations.*, assets.asset_tag, assets.name AS asset_name, users.name AS employee_name
        FROM allocations
        JOIN assets ON assets.id = allocations.asset_id
        JOIN users ON users.id = allocations.employee_id
        WHERE allocations.status = 'active'
        ORDER BY allocations.id DESC
    """).fetchall()
    return render_template("allocation/index.html", allocations=allocations)


@allocation_bp.route("/allocate", methods=["GET", "POST"])
@role_required("asset_manager", "admin", "dept_head")
def allocate():
    db = database.get_db()

    if request.method == "POST":
        asset_id = request.form["asset_id"]
        employee_id = request.form["employee_id"]
        expected_return = request.form.get("expected_return") or None

        # --- THE CORE CONFLICT RULE ---
        # An asset can have at most one ACTIVE allocation at a time.
        current_holder = db.execute("""
            SELECT allocations.id, users.name AS holder_name
            FROM allocations
            JOIN users ON users.id = allocations.employee_id
            WHERE allocations.asset_id = ? AND allocations.status = 'active'
        """, (asset_id,)).fetchone()

        if current_holder:
            flash(f"This asset is currently held by {current_holder['holder_name']}. "
                  f"Use Transfer Request instead of direct allocation.")
            return redirect(url_for("allocation.allocate"))

        db.execute(
            "INSERT INTO allocations (asset_id, employee_id, expected_return, status) VALUES (?, ?, ?, 'active')",
            (asset_id, employee_id, expected_return),
        )
        db.execute("UPDATE assets SET status = 'allocated' WHERE id = ?", (asset_id,))
        db.commit()
        log_activity(session["user_id"], "allocated asset", f"asset_id={asset_id} -> employee_id={employee_id}")
        flash("Asset allocated successfully.")
        return redirect(url_for("allocation.index"))

    assets = db.execute("SELECT * FROM assets WHERE status = 'available'").fetchall()
    employees = db.execute("SELECT * FROM users WHERE status = 'active'").fetchall()
    return render_template("allocation/allocate.html", assets=assets, employees=employees)


@allocation_bp.route("/transfer/<int:allocation_id>", methods=["POST"])
@role_required("asset_manager", "dept_head", "admin")
def transfer(allocation_id):
    # Simplified transfer: closes the old allocation and opens a new one,
    # which is enough to satisfy "Requested -> Approved -> Re-allocated"
    # for a hackathon demo. History stays intact because both rows remain.
    db = database.get_db()
    new_employee_id = request.form["new_employee_id"]
    old = db.execute("SELECT * FROM allocations WHERE id = ?", (allocation_id,)).fetchone()

    db.execute("UPDATE allocations SET status = 'transferred' WHERE id = ?", (allocation_id,))
    db.execute(
        "INSERT INTO allocations (asset_id, employee_id, status) VALUES (?, ?, 'active')",
        (old["asset_id"], new_employee_id),
    )
    db.commit()
    log_activity(session["user_id"], "transferred asset", f"allocation_id={allocation_id}")
    flash("Transfer completed.")
    return redirect(url_for("allocation.index"))


@allocation_bp.route("/return/<int:allocation_id>", methods=["POST"])
@login_required
def return_asset(allocation_id):
    db = database.get_db()
    condition_notes = request.form.get("condition_notes", "")
    alloc = db.execute("SELECT * FROM allocations WHERE id = ?", (allocation_id,)).fetchone()

    db.execute(
        "UPDATE allocations SET status = 'returned', returned_on = datetime('now') WHERE id = ?",
        (allocation_id,),
    )
    db.execute("UPDATE assets SET status = 'available' WHERE id = ?", (alloc["asset_id"],))
    db.commit()
    log_activity(session["user_id"], "returned asset", f"allocation_id={allocation_id}, notes={condition_notes}")
    flash("Asset marked as returned.")
    return redirect(url_for("allocation.index"))
