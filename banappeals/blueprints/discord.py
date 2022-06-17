from flask import Blueprint, current_app as app


bp = Blueprint("discord", __name__)


def get_user_by_id(id: int) -> dict:
    return app.discord.bot_request(route=f"/users/{id}", method="GET")


def is_user_banned(guild_id: str, user_id: str):
    result = app.discord.bot_request(route=f"/guilds/{guild_id}/bans/{user_id}", method="GET")
    return result if result.get("user") else False


def unban_user(guild_id: str, user_id: str):
    result = app.discord.bot_request(route=f"/guilds/{guild_id}/bans/{user_id}", method="DELETE")
    return False if result.get("user") else True
