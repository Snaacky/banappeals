from functools import wraps

from flask import Blueprint, current_app as app, redirect, flash, url_for
from flask_discord import requires_authorization, AccessDenied, Unauthorized

from banappeals.blueprints.discord import is_staff


bp = Blueprint("auth", __name__)


@bp.route("/login")
def login():
    return app.discord.create_session(scope=["identify", "guilds.join"])


@bp.route("/logout")
@requires_authorization
def logout():
    app.discord.revoke()
    return redirect(url_for("views.index"))


@bp.route("/callback")
def callback():
    try:
        app.discord.callback()
    except AccessDenied:
        return redirect(url_for("views.index"))
    return redirect(url_for("views.index"))


def staff_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = app.discord.fetch_user()
        if is_staff(user.id):
            return f(*args, **kwargs)

        flash("You do not have permission to access that.", "danger")
        return redirect(url_for("views.index"))

    return decorated_function


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("auth.login"))
