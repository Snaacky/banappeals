from datetime import datetime
from functools import wraps

from flask import Blueprint, current_app as app, redirect, flash
from flask.helpers import url_for
from flask_discord import Unauthorized
from geoip import geolite2

from banappeals import database as db

bp = Blueprint("utils", __name__)


def get_discord_user_by_id(id: int) -> dict:
    """
    Returns Discord user data from the API for the snowflake provided.
    """
    return app.discord.bot_request(route=f"/users/{id}", method="GET")


def is_user_banned(guild_id: str, user_id: str):
    result = app.discord.bot_request(route=f"/guilds/{guild_id}/bans/{user_id}", method="GET")
    return result if result.get("user") else False


def unban_user(guild_id: str, user_id: str):
    result = app.discord.bot_request(route=f"/guilds/{guild_id}/bans/{user_id}", method="DELETE")
    return False if result.get("user") else True


@app.add_template_filter
def get_reviewer_from_discord_id(id: int) -> dict:
    """
    Returns a reviewer's user data from the database for the ID provided.
    """
    return db.get_reviewer(id=id)


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    """
    Redirects unauthorized users who access endpoints with the
    @requires_authorization decorator back to the root domain.
    """
    return redirect(url_for("auth.login"))


@app.add_template_filter
def format_timestamp(s):
    """
    Jinja2 filter used to convert Unix timestamps to a UTC format string.
    """
    return datetime.utcfromtimestamp(s).strftime("%m/%d/%Y at %H:%M UTC")


@app.add_template_filter
def ip2geo(ip):
    """
    Jinja2 filter used for resolving the country from an IP address.
    """
    try:
        return geolite2.lookup(ip).get_info_dict()["country"]["names"]["en"]
    except Exception:
        return "N/A"


def editors_only(f):
    """
    Declared as a decorator, @editors_only is used to prevent regular
    authenticated users (application submitters) from being able to
    manipulate the API endpoints if they were to discover them by
    redirecting any unauthenticated requests back to the home page.

    This decorator should be attached to any function that does
    a critical management process such as approving or denying
    applications.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.discord.fetch_user().id not in app.config["EDITORS"]:
            flash("You do not have permission to access that.", "danger")
            return redirect(url_for("views.index"))
        return f(*args, **kwargs)

    return decorated_function
