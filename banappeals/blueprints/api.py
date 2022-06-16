import time

from flask import Blueprint, current_app as app, redirect, request, flash
from flask.helpers import url_for
from flask_discord import requires_authorization

import database
import blueprints.utils as utils

bp = Blueprint('api', __name__)


@bp.route("/submit", methods=["POST"])
@requires_authorization
def submit():
    """
    API endpoint for the user's browser to submit their application
    form data to the backend server for processing.

    Strips any runoff data longer than the client-side form allows,
    checks to make sure all the required variables were in the POST,
    and inserts the data into the database.
    """

    # Don't allow users to submit more than one application.
    user = app.discord.fetch_user()

    # Don't allow users to submit multiple applications per user.
    if database.get_application_id_from_discord_id(user.id):
        flash("You already submitted an application.", "danger")
        return redirect(url_for("views.index"))

    # Add all of the POST'd variables into a dictionary for processing.
    data = {
        "email_address": request.form.get("emailAddress")[0:100],
        "reddit_username": request.form.get("redditUsername")[0:20],
        "referral": request.form.get("whereDidYouHear")[0:1500],
        "about_me": request.form.get("tellUsAboutYourself")[0:1500],
        "expectations": request.form.get("whatDoYouExpect")[0:1500],
        "already_known": request.form.get("whatDoYouKnowAbout")[0:1500],
        "why_should_be_invited": request.form.get("whyShouldYouBeOffered")[0:1500],
        "currently_watching": request.form.get("whatAnimeAreYouWatching")[0:1500],
        "favorite_anime": request.form.get("whatIsYourFavoriteAnime")[0:1500],
        "do_you_have_a_list": request.form.get("doYouHaveAList")[0:1500]
    }

    # Check if any of the POST variables were missing and return HTTP 400 if so.
    if not any([
        data["email_address"], data["reddit_username"], data["referral"],
        data["about_me"], data["expectations"], data["already_known"],
        data["why_should_be_invited"], data["currently_watching"],
        data["favorite_anime"]
    ]):
        flash("POST data was missing from your submission.", "danger")
        return redirect(url_for("views.index"))

    # Attempts to get the IP address from the header or falls back to the
    # connecting IP address.
    ip_address = request.headers.get("X-Real-IP") or request.remote_addr

    # Check if a Proxycheck API key was set, if so, enable VPN detectiong.
    if app.config["PROXYCHECK_KEY"]:
        result = utils.check_if_ip_is_proxy(ip_address, app.config["PROXYCHECK_KEY"])

        # If the result is True, the IP used was a proxy.
        if result:
            flash("We do not allow applications from proxies, VPNs, or Tor.", "danger")
            return redirect(url_for("views.index"))

        # If the result is None, an issue occurred with the Proxycheck API.
        if result is None:
            flash("An error occurred, please try again later.", "danger")
            return redirect(url_for("views.index"))

    # Further define the various variables we'll need to insert into the database.
    user = app.discord.fetch_user()
    data["username"] = user.name
    data["discriminator"] = user.discriminator
    data["avatar"] = user.avatar_hash
    data["discord_id"] = user.id
    data["timestamp"] = int(time.time())
    data["ip_address"] = ip_address
    data["application_status"] = None
    data["reviewed_by"] = None

    # Insert the received POST data into the database and return HTTP 200.
    database.insert_data_into_db(table="applications", data=data)
    flash("Your application has been successfully submitted.", "info")
    return redirect(url_for("views.index"))


@bp.route("/approve/<id>")
@requires_authorization
@utils.editors_only
def accept_application(id):
    """
    API endpoint for the editors to accept an application. Updates
    the entry in the database and then attempts to redirect to the
    next application. If no newer applications exists, will redirect
    back to application that was just accepted.
    """

    # Fetches the Discord user object of the reviewer.
    reviewer = app.discord.fetch_user()

    # Updates the entry in the database as approved.
    database.update_application_status(id, status=True, reviewed_by=reviewer.id)

    # Redirects back to the last application if no newer exists.
    next = database.get_application(int(id) + 1)
    if not next:
        return redirect(url_for("views.review"))

    # Otherwise, redirects to the next application as expected.
    return redirect(f"/review/{int(id) + 1}")


@bp.route("/reject/<id>")
@requires_authorization
@utils.editors_only
def reject_application(id):
    """
    API endpoint for the editors to reject an application. Updates
    the entry in the database and then attempts to redirect to the
    next application. If no newer applications exists, will redirect
    back to application that was just accepted.
    """

    # Fetches the Discord user object of the reviewer.
    reviewer = app.discord.fetch_user()

    # Updates the entry in the database as approved.
    database.update_application_status(id, status=False, reviewed_by=reviewer.id)

    # Redirects back to the last application if no newer exists.
    next = database.get_application(int(id) + 1)
    if not next:
        return redirect(url_for("views.index"))

    # Otherwise, redirects to the next application as expected.
    return redirect(f"/review/{int(id) + 1}")


@bp.route("/search/id/<id>")
@requires_authorization
@utils.editors_only
def search_application_by_id(id):
    """
    API endpoint to attempt to search for an application by the
    applicants Discord ID. If the applicant doesn't exist,
    redirects back to the review panel home page.
    """
    # Attempt to lookup the SQLite ID by the Discord ID.
    id = database.get_application_id_from_discord_id(id)

    # If we were unable to find anything, flash an error and redirect.
    if not id:
        flash("Unable to find an application for that Discord ID.", "info")
        return redirect(url_for("views.review"))

    # Otherwise, redirect to the application that was found.
    return redirect(f"/review/{id}")


@bp.route("/search/email/<email>")
@requires_authorization
@utils.editors_only
def search_application_by_email(email):
    """
    API endpoint to attempt to search for an application by the
    applicants email address. If the applicant doesn't exist,
    redirects back to the management panel home page.
    """

    # Attempt to lookup the SQLite ID by the email address.
    id = database.get_application_id_from_email(email)

    # If we were unable to find anything, flash an error and redirect.
    if not id:
        flash("Unable to find an application for that email.", "info")
        return redirect(url_for("views.review"))

    # Otherwise, redirect to the application that was found.
    return redirect(f"/review/{id}")


@bp.route("/search/username/<username>")
@requires_authorization
@utils.editors_only
def search_application_by_username(username):
    """
    API endpoint to attempt to search for an application by the
    applicants Discord username. If the applicant doesn't exist,
    redirects back to the management panel home page.
    """

    # Attempt to lookup the SQLite ID by the email address.
    username, discriminator = username.split("#")
    id = database.get_application_id_from_discord_user(
        username=username,
        discriminator=discriminator
    )

    # If we were unable to find anything, flash an error and redirect.
    if not id:
        flash("Unable to find an application for that username.", "info")
        return redirect(url_for("views.review"))

    # Otherwise, redirect to the application that was found.
    return redirect(f"/review/{id}")


@bp.route("/join")
@requires_authorization
def join_server():
    """
    API endpoint for accepted users to be able to join the server
    and redirects them to the server's Discord URL after adding them.

    Does some basic checks to make sure the application was actually
    accepted instead of pending or rejected.
    """
    # Get the current Discord user.
    user = app.discord.fetch_user()

    # Using the user's Discord ID, get the application ID.
    id = database.get_application_id_from_discord_id(user.id)

    # Request the application data from the database using the application ID.
    application = database.get_application(id)

    # Redirect the user back if they don't have an accepted application.
    if not application or not application["application_status"]:
        return redirect(url_for("views.status"))

    # Otherwise, add the user to the server with the bot application.
    user.add_to_guild(guild_id=app.config["GUILD_ID"])

    # Redirect the users browser to the Discord URL for the server.
    return redirect(f"https://discord.com/channels/{app.config['GUILD_ID']}")
