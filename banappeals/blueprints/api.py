import time

from flask import Blueprint, current_app as app, redirect, request, flash
from flask.helpers import url_for
from flask_discord import requires_authorization

from banappeals import database as db
from banappeals.blueprints.auth import staff_only
from banappeals.blueprints.discord import get_ban
from banappeals.modals import Appeal


bp = Blueprint("api", __name__)


@bp.route("/submit", methods=["POST"])
@requires_authorization
def submit():
    user = app.discord.fetch_user()

    if db.get_appeal(discord_id=user.id):
        flash("You already submitted an application.", "danger")
        return redirect(url_for("views.index"))

    if not any(
        [
            request.form.get("whyWereYouBanned"),
            request.form.get("whyShouldYouBeUnbanned"),
            request.form.get("anythingElseToAdd"),
        ]
    ):
        flash("POST data was missing from your submission.", "danger")
        return redirect(url_for("views.index"))

    appeal = Appeal(
        discord_user=f"{user.name}#{user.discriminator}",
        discord_id=user.id,
        ban_reason=get_ban(user.id)["reason"],
        ban_explanation=request.form.get("whyWereYouBanned")[0:1500],
        unban_explanation=request.form.get("whyShouldYouBeUnbanned")[0:1500],
        additional_comments=request.form.get("anythingElseToAdd")[0:1500],
        status=None,
        reviewer=None,
        timestamp=int(time.time()),
        ip_address=request.headers.get("X-Real-IP") or request.remote_addr,
    )
    appeal.save()

    flash("Your appeal has been successfully submitted.", "info")
    return redirect(url_for("views.index"))


@bp.route("/review/<operation>/<id>")
@requires_authorization
@staff_only
def review_appeal(operation, id):
    reviewer = app.discord.fetch_user()

    appeal = Appeal()
    data = db.get_appeal(id)
    for key in data:
        setattr(appeal, key, data[key])

    match operation:
        case "approve":
            appeal.approve(reviewer.id)
        case "reject":
            appeal.reject(reviewer.id)
        case _:
            flash("An invalid operation was provided for the application review.", "danger")
            return redirect(url_for("views.overview"))


@bp.route("/search/id/<id>")
@requires_authorization
@staff_only
def get_appeal_by_id(id):
    id = db.get_appeal(discord_id=id)
    if not id:
        flash("Unable to find an application for that Discord ID.", "info")
        return redirect(url_for("views.overview"))
    return redirect(f"/review/{id}")


@bp.route("/join")
@requires_authorization
def join_server():
    user = app.discord.fetch_user()
    appeal = db.get_appeal(discord_id=user.id)
    if not appeal or not appeal["status"]:
        return redirect(url_for("views.status"))
    user.add_to_guild(guild_id=app.config["GUILD_ID"])
    return redirect(f"https://discord.com/channels/{app.config['GUILD_ID']}")
