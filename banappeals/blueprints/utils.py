import json
import urllib3
from datetime import datetime
from functools import wraps

from flask import Blueprint, current_app as app, redirect, flash
from flask.helpers import url_for
from flask_discord import Unauthorized
from geoip import geolite2

from banappeals.database import Database as db

bp = Blueprint("utils", __name__)


def get_discord_user_by_id(id: int) -> dict:
    """
    Used as a utility to convert a Discord snowflake (ID) into an
    object containing all of the data about the user returned from the
    Discord API.
    """
    return app.discord.bot_request(route=f"/users/{id}", method="GET")


@app.add_template_filter
def get_reviewer_from_discord_id(id: int) -> dict:
    """
    Used as a utility to convert a Discord snowflake (ID) into an
    object containing all of the data about the user returned from the
    Discord API.
    """
    return db().get_reviewer(id=id)


def check_if_ip_is_proxy(ip_address: str, api_key: str):
    """
    Used as a utility during /submit POST, check_if_ip_is_proxy()
    uses the Proxycheck to attempt to check if the IP address
    that submitted the application was a proxy/VPN/Tor and returns
    True or False accordingly.
    """
    urllib3.disable_warnings()
    http = urllib3.PoolManager()

    if ip_address.startswith(("192.", "172.", "127.")):
        return False

    r = http.request(method="GET", url=f"https://proxycheck.io/v2/{ip_address}?key={api_key}&vpn=1")
    if r.status != 200:
        print(f"An error occurred connecting to the Proxycheck API: {r.data.decode('utf-8')}")
        return None

    response = json.loads(r.data.decode("utf-8"))
    return True if response[ip_address]["proxy"] == "yes" else False


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    """
    Declared as an error handler, redirect_unauthorized will redirect
    unauthorized users who attempt to interact with an endpoint with
    the @requires_authorization decorator back to the root of the
    domain.
    """
    return redirect(url_for("auth.login"))


@app.add_template_filter
def format_timestamp(s):
    """
    Declared as a Jinja2 filter, format_timestamp is used to convert
    Unix epoch timestamps stored in the database to a human readable
    string of the time in UTC format.
    """
    return datetime.utcfromtimestamp(s).strftime("%m/%d/%Y at %H:%M UTC")


@app.add_template_filter
def ip2geo(ip):
    """
    Declared as Jinja2 filter, ip2geo is used to lookup the country
    for a specific IP address.
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


def admins_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.discord.fetch_user().id not in app.config["ADMINS"]:
            flash("You do not have permission to access that.", "danger")
            return redirect(url_for("views.index"))
        return f(*args, **kwargs)

    return decorated_function
