import os
import random
import string

from flask import Flask
from flask_discord import DiscordOAuth2Session

from banappeals.blueprints import views, auth, api, utils
from banappeals.database import Database


def create_app():
    app = Flask(__name__)

    if not os.path.isfile(os.path.join("config", ".flask_secret")):
        with open(os.path.join("config", ".flask_secret"), "w") as f:
            f.write(''.join(random.choices(string.ascii_uppercase + string.digits, k=12)))

    with open(os.path.join("config", ".flask_secret"), "rb") as secret:
        app.secret_key = secret.read()

    app.config["DISCORD_CLIENT_ID"] = os.environ.get("DISCORD_CLIENT_ID")
    app.config["DISCORD_CLIENT_SECRET"] = os.environ.get("DISCORD_CLIENT_SECRET")
    app.config["DISCORD_REDIRECT_URI"] = os.environ.get("DISCORD_REDIRECT_URI")
    app.config["DISCORD_BOT_TOKEN"] = os.environ.get("DISCORD_BOT_TOKEN")

    with app.app_context():
        app.register_blueprint(views.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(utils.bp)
        app.discord = DiscordOAuth2Session(app)

    Database().setup()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
