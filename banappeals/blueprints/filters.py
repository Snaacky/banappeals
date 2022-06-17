from datetime import datetime

from flask import Blueprint, current_app as app
from geoip import geolite2

from banappeals import database as db

bp = Blueprint("filters", __name__)


@app.add_template_filter
def get_reviewer_from_discord_id(id: int) -> dict:
    return db.get_reviewer(id=id)


@app.add_template_filter
def format_timestamp(s):
    return datetime.utcfromtimestamp(s).strftime("%m/%d/%Y at %H:%M UTC")


@app.add_template_filter
def ip2geo(ip):
    try:
        return geolite2.lookup(ip).get_info_dict()["country"]["names"]["en"]
    except Exception:
        return "N/A"
