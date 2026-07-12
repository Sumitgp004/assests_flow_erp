from functools import wraps
from flask import session, redirect, url_for
import database


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """Usage: @role_required('admin', 'asset_manager')"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                return "Forbidden: your role cannot access this page.", 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def current_user():
    if "user_id" not in session:
        return None
    db = database.get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()


def log_activity(user_id, action, target=None):
    db = database.get_db()
    db.execute(
        "INSERT INTO activity_log (user_id, action, target) VALUES (?, ?, ?)",
        (user_id, action, target),
    )
    db.commit()
