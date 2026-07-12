from flask import Blueprint, render_template, request, redirect, url_for
import database
from routes.utils import role_required, log_activity
from flask import session

org_bp = Blueprint("org", __name__, template_folder="../templates/org_setup", url_prefix="/org")


@org_bp.route("/")
@role_required("admin")
def index():
    db = database.get_db()
    departments = db.execute("SELECT * FROM departments").fetchall()
    categories = db.execute("SELECT * FROM asset_categories").fetchall()
    employees = db.execute("SELECT * FROM users").fetchall()
    return render_template(
        "org_setup/index.html",
        departments=departments, categories=categories, employees=employees,
    )


@org_bp.route("/departments/new", methods=["POST"])
@role_required("admin")
def new_department():
    db = database.get_db()
    name = request.form["name"]
    parent_id = request.form.get("parent_id") or None
    db.execute("INSERT INTO departments (name, parent_id) VALUES (?, ?)", (name, parent_id))
    db.commit()
    return redirect(url_for("org.index"))


@org_bp.route("/categories/new", methods=["POST"])
@role_required("admin")
def new_category():
    db = database.get_db()
    name = request.form["name"]
    db.execute("INSERT INTO asset_categories (name) VALUES (?)", (name,))
    db.commit()
    return redirect(url_for("org.index"))


@org_bp.route("/promote/<int:user_id>", methods=["POST"])
@role_required("admin")
def promote(user_id):
    # The ONLY place in the app where a role can change.
    new_role = request.form["role"]
    db = database.get_db()
    db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    db.commit()
    log_activity(session["user_id"], "promoted user", f"user_id={user_id} to role={new_role}")
    return redirect(url_for("org.index"))

# TODO (P2): edit/deactivate department, category-specific extra fields
