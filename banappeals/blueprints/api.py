import time

from flask import Blueprint, current_app as app, redirect, request, flash
from flask.helpers import url_for
from flask_discord import requires_authorization

from banappeals.blueprints import utils
from banappeals import database as db
from banappeals.blueprints.auth import staff_only
from banappeals.blueprints.discord import get_ban


bp = Blueprint("api", __name__)


@bp.route("/submit", methods=["POST"])
@requires_authorization
def submit():
    user = app.discord.fetch_user()

    if db.get_application_id_from_discord_id(user.id):
        flash("You already submitted an application.", "danger")
        return redirect(url_for("views.index"))

    data = {
        "ban_time": request.form.get("whenWereYouBanned")[0:1500],
        "ban_reason_user": request.form.get("whyWereYouBanned")[0:1500],
        "unban_reason_user": request.form.get("whyShouldYouBeUnbanned")[0:1500],
        "additional_comments": request.form.get("anythingElseToAdd")[0:1500],
    }

    if not any(
        [
            data["ban_time"],
            data["ban_reason_user"],
            data["unban_reason_user"],
            data["additional_comments"],
        ]
    ):
        flash("POST data was missing from your submission.", "danger")
        return redirect(url_for("views.index"))

    data["username"] = f"{user.name}#{user.discriminator}"
    data["ban_reason"] = utils.is_user_banned(974468300304171038, user.id)["reason"]
    data["discord_id"] = user.id
    data["timestamp"] = int(time.time())
    data["ip_address"] = request.headers.get("X-Real-IP") or request.remote_addr
    data["application_status"] = None
    data["reviewed_by"] = None

    db.insert_data_into_db(table="applications", data=data)
    flash("Your appeal has been successfully submitted.", "info")
    return redirect(url_for("views.index"))


@bp.route("/review/<operation>/<id>")
@requires_authorization
@staff_only
def review_application(operation, id):
    reviewer = app.discord.fetch_user()
    match operation:
        case "approve":
            db.update_application_status(id, status=True, reviewed_by=reviewer.id)
        case "reject":
            db.update_application_status(id, status=False, reviewed_by=reviewer.id)
        case _:
            flash("An invalid operation was provided for the application review.", "danger")
            return redirect(url_for("views.overview"))


@bp.route("/search/id/<id>")
@requires_authorization
@staff_only
def search_application_by_id(id):
    id = db.get_application_id_from_discord_id(id)
    if not id:
        flash("Unable to find an application for that Discord ID.", "info")
        return redirect(url_for("views.review"))
    return redirect(f"/review/{id}")


@bp.route("/join")
@requires_authorization
def join_server():
    user = app.discord.fetch_user()
    id = db.get_application_id_from_discord_id(user.id)
    application = db.get_application(id)
    if not application or not application["application_status"]:
        return redirect(url_for("views.status"))
    user.add_to_guild(guild_id=app.config["GUILD_ID"])
    return redirect(f"https://discord.com/channels/{app.config['GUILD_ID']}")
