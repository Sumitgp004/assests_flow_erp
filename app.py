from flask import Flask, render_template, session, redirect, url_for
import database
from routes.auth import auth_bp
from routes.org import org_bp
from routes.assets import assets_bp
from routes.allocation import allocation_bp
from routes.booking import booking_bp
from routes.maintenance import maintenance_bp
from routes.logs import logs_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "hackathon-secret-change-me"  # fine for a demo, not for real prod

    database.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(allocation_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(logs_bp)

    @app.route("/")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        db = database.get_db()
        kpis = {
            "available": db.execute("SELECT COUNT(*) c FROM assets WHERE status='available'").fetchone()["c"],
            "allocated": db.execute("SELECT COUNT(*) c FROM assets WHERE status='allocated'").fetchone()["c"],
            "maintenance": db.execute("SELECT COUNT(*) c FROM assets WHERE status='maintenance'").fetchone()["c"],
            "active_bookings": db.execute(
                "SELECT COUNT(*) c FROM bookings WHERE status IN ('upcoming','ongoing')"
            ).fetchone()["c"],
            "overdue": db.execute(
                "SELECT COUNT(*) c FROM allocations WHERE status='active' "
                "AND expected_return IS NOT NULL AND expected_return < date('now')"
            ).fetchone()["c"],
        }
        return render_template("dashboard/index.html", kpis=kpis)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
