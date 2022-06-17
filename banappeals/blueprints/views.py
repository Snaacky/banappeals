from flask import Blueprint, current_app as app, redirect, flash, url_for, render_template
from flask_discord import requires_authorization

import banappeals.blueprints.utils as utils
from banappeals import database as db
from banappeals.blueprints.auth import staff_only


bp = Blueprint("views", __name__)


@bp.route("/")
def index():
    user = banned = None
    if app.discord.authorized:
        user = app.discord.fetch_user()
        banned = utils.is_user_banned(guild_id=974468300304171038, user_id=user.id)
    return render_template(template_name_or_list="index.htm", user=user, banned=banned)


@bp.route("/review", defaults={"id": None})
@bp.route("/review/<id>")
@requires_authorization
@staff_only
def review(id):
    if not id:
        return redirect(url_for("views.overview"))

    application = db.get_application(id)
    previous_app, next_app = db.get_surrounding_applications(application["id"])
    applicant = utils.get_discord_user_by_id(application["discord_id"])

    return render_template(
        template_name_or_list="review.htm",
        stats=db.get_stats(),
        reviewer=app.discord.fetch_user(),
        applicant=applicant,
        application=application,
        previous_app=previous_app,
        next_app=next_app,
    )


@bp.route("/status")
@requires_authorization
def status():
    user = app.discord.fetch_user()

    id = db.get_application_id_from_discord_id(user.id)
    if not id:
        flash("You have not submitted an application.", "danger")
        return redirect(url_for("views.index"))

    return render_template(template_name_or_list="status.htm", application=db.get_application(id))


@bp.route("/overview")
@requires_authorization
@staff_only
def overview():
    return render_template(
        template_name_or_list="overview.htm",
        stats=db.get_stats(),
        reviewer=app.discord.fetch_user(),
        applications=db.get_reviewed_applications(),
    )
