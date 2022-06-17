import os
from collections import OrderedDict
from typing import Optional

import dataset
from dataset import Database


def get() -> Database:
    return dataset.connect(f"sqlite:///{os.path.join('config', 'data.db')}")


def setup() -> None:
    db = get()
    applications = db.create_table("applications")
    applications.create_column("discord_user", db.types.text)
    applications.create_column("discord_id", db.types.bigint)
    applications.create_column("ban_reason", db.types.text)
    applications.create_column("ban_explanation", db.types.text)
    applications.create_column("unban_explanation", db.types.text)
    applications.create_column("additional_comments", db.types.text)
    applications.create_column("status", db.types.boolean)
    applications.create_column("reviewer", db.types.bigint)
    applications.create_column("timestamp", db.types.bigint)
    applications.create_column("ip_address", db.types.bigint)
    db.commit()
    db.close()


def check_if_app_exists(discord_id: int) -> bool:
    db = get()
    entry = db["applications"].find_one(discord_id=discord_id)
    db.close()
    return True if entry else False


def insert_data_into_db(table: str, data: dict) -> None:
    db = get()
    db[table].insert(data)
    db.commit()
    db.close()


def get_stats() -> dict:
    db = get()
    results = list(db.query("SELECT * from applications"))
    stats = {"pending": 0, "total": len(results), "accepted": 0, "denied": 0}
    for row in results:
        if row["application_status"] is None:
            stats["pending"] += 1
        if row["application_status"]:
            stats["accepted"] += 1
        if not row["application_status"]:
            stats["denied"] += 1
    return stats


def get_application(id) -> OrderedDict:
    db = get()
    result = db["applications"].find_one(id=id)
    db.close()
    return result


def update_application_status(id: int, status: bool, reviewed_by: str) -> None:
    db = get()
    application = db["applications"].find_one(id=id)
    application["application_status"] = status
    application["reviewed_by"] = reviewed_by
    db["applications"].update(application, ["id"])
    db.commit()
    db.close()


def get_application_id_from_discord_id(id: int) -> Optional[int]:
    db = get()
    application = db["applications"].find_one(discord_id=id)
    db.close()
    return application["id"] if application else None


def get_application_id_from_ip(ip_address: str) -> Optional[int]:
    db = get()
    application = db["applications"].find_one(ip_address=ip_address)
    db.close()
    return application["id"] if application else None


def get_all_applications():
    db = get()
    results = list(db.query("SELECT * from applications"))
    db.close()
    return results


def get_reviewed_applications():
    db = get()
    results = list(db["applications"].find(application_status={"not": None}))
    db.close()
    return results
