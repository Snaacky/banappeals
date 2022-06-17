from flask import Blueprint, current_app as app, redirect

from flask.helpers import url_for
from flask_discord import requires_authorization, AccessDenied

from banappeals import database as db


bp = Blueprint("auth", __name__)


@bp.route("/login")
def login():
    """
    This endpoint creates a Discord OAuth session and redirects
    the user to the Discord login page for authentication with
    the Discord application we created.
    """
    return app.discord.create_session(scope=["identify", "guilds.join"])


@bp.route("/logout")
@requires_authorization
def logout():
    """
    This endpoint kills the Discord OAuth session and redirects
    the user to the root of the domain.
    """
    app.discord.revoke()
    return redirect(url_for("views.index"))


@bp.route("/callback")
def callback():
    """
    This endpoint is handled by Flask-Discord but is the callback
    where the Discord authentication service interacts with our web
    app post-authentication.
    """
    try:
        app.discord.callback()
    except AccessDenied:
        return redirect(url_for("views.index"))

    user = app.discord.fetch_user()

    # Redirects to the home page after logging in.
    return redirect(url_for("views.index"))
