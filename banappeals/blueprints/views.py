from flask import Blueprint, current_app as app, redirect, flash
from flask.templating import render_template
from flask_discord import requires_authorization

import banappeals.blueprints.utils as utils
from banappeals.database import Database as db

bp = Blueprint("views", __name__)


@bp.route("/")
def index():
    """
    This endpoint is the viewport for the index of the applications
    web app.

    If the user is not authenticated, it will render a button to
    authenticate with Discord.

    If the user is authenticated and has not submitted an application,
    it will render the application form. Otherwise it will render a
    message letting them know they've already submitted their
    application.

    If the user is authenticated and their Discord ID is listed under
    the EDITORS environment variable, it will render a link to the
    management panel.
    """
    if app.discord.authorized:
        user = app.discord.fetch_user()
        status = db().check_if_app_exists(user.id)

    return render_template(
        template_name_or_list="index.htm",
        user=user or None,
        status=status or None,
        editors=app.config["EDITORS"],
        accepting=app.config["ACCEPTING"],
        closed_message=app.config["CLOSED_MESSAGE"],
    )


@bp.route("/review", defaults={"id": None})
@bp.route("/review/<id>")
@requires_authorization
@utils.editors_only
def review(id):
    """
    This endpoint is the viewport for the application reviewer
    management panel. It queries the database for the specific
    application to render and the statistics for the review
    panel and renders the viewport.

    The application to render is specified with the id parameter.
    If the /review endpoint is used with no ID specified, the web
    app will default the ID value to None and return the first
    application.
    """

    if id:
        application = db().get_application(id)
    else:
        application = db().get_oldest_pending_application()

    previous_app, next_app = db().get_surrounding_applications(application["id"])
    applicant = utils.get_discord_user_by_id(application["discord_id"])

    return render_template(
        template_name_or_list="review.htm",
        stats=db().get_stats(),  # Get the current management panel statistics.
        reviewer=app.discord.fetch_user(),  # Get the reviewer's Discord profile.
        applicant=applicant,  # Get the applicant's Discord profile.
        application=application,  # Passes the application fetched from the database.
        previous_app=previous_app,
        next_app=next_app,
    )


@bp.route("/status")
@requires_authorization
def status():
    """
    This endpoint is the viewport for viewing the current status of the
    application by the end user. It queries the database for the users
    application and renders it along with the current status (approved,
    denied, pending) of their application.

    If the user attempts to view the endpoint without having submitted
    an application, it will redirect the user to the root of the
    domain.

    If the application is accepted, the endpoint will additionally
    render a Discord join server button that allows the user to join
    the Discord server via OAuth.
    """
    # Get the current Discord user.
    user = app.discord.fetch_user()

    # Using the user's Discord ID, get the application SQLite ID.
    id = db().get_application_id_from_discord_id(user.id)

    # Redirect back to the application if no application submitted.
    if not id:
        flash("You have not submitted an application.", "danger")
        return redirect("/")

    # Request the application from the database using the SQLite ID.
    application = db().get_application(id)

    return render_template(template_name_or_list="status.htm", application=application)


@bp.route("/overview")
@requires_authorization
@utils.editors_only
def overview():
    return render_template(
        template_name_or_list="overview.htm",
        stats=db().get_stats(),
        reviewer=app.discord.fetch_user(),
        applications=db().get_reviewed_applications(),
    )


@bp.route("/admin")
@requires_authorization
@utils.admins_only
def admin():
    return render_template(template_name_or_list="admin.htm", stats=db().get_stats(), reviewer=app.discord.fetch_user())
