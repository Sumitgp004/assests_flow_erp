from flask import Blueprint, render_template
import database
from routes.utils import login_required

logs_bp = Blueprint("logs", __name__, template_folder="../templates/logs", url_prefix="/logs")


@logs_bp.route("/")
@login_required
def index():
    db = database.get_db()
    entries = db.execute("""
        SELECT activity_log.*, users.name AS user_name
        FROM activity_log LEFT JOIN users ON users.id = activity_log.user_id
        ORDER BY timestamp DESC
    """).fetchall()
    return render_template("logs/index.html", entries=entries)
