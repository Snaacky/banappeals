from flask import Blueprint, current_app as app


bp = Blueprint("discord", __name__)


def get_ban(user_id: str):
    route = f"/guilds/{app.config['guild']['guild_id']}/bans/{user_id}"
    result = app.discord.bot_request(route=route, method="GET")
    return result if result.get("user") else False


def unban_user(user_id: str):
    route = f"/guilds/{app.config['guild']['guild_id']}/bans/{user_id}"
    result = app.discord.bot_request(route=route, method="DELETE")
    return False if result.get("user") else True
