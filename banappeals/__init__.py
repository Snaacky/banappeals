import os

from flask import Flask
from flask_discord import DiscordOAuth2Session
from pyaml_env import parse_config

from banappeals import database as db


def create_app():
    app = Flask(__name__)

    # TODO: Add check to verify all of the values used below exist in the config.
    app.config = app.config | parse_config(os.path.join(os.getcwd(), "config.yml"))
    app.secret_key = app.config["flask"]["secret"]
    app.config["DISCORD_CLIENT_ID"] = app.config["discord"]["id"]
    app.config["DISCORD_CLIENT_SECRET"] = app.config["discord"]["secret"]
    app.config["DISCORD_REDIRECT_URI"] = app.config["discord"]["callback"]
    app.config["DISCORD_BOT_TOKEN"] = app.config["discord"]["token"]

    with app.app_context():
        from banappeals.blueprints import api, auth, discord, filters, views

        app.register_blueprint(api.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(discord.bp)
        app.register_blueprint(filters.bp)
        app.register_blueprint(views.bp)
        app.discord = DiscordOAuth2Session(app)

    # TODO: Move to MariaDB later because SQLite always has issues with dataset.
    db.setup()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
