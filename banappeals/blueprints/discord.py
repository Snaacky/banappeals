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


def is_staff() -> bool:
    route = f"/users/@me/guilds/{app.config['guild']['guild_id']}/member"
    member = app.discord.request(route=route, method="GET")

    return True if app.config["guild"]["roles"]["staff"] in member["roles"] else False
