from collections import OrderedDict
from typing import Optional

import dataset
from dataset import Database


def get() -> Database:
    """
    Returns an active connection to the database.
    """
    return dataset.connect("sqlite:///config/data.db")


def setup() -> None:
    """
    Connects to the database and attempts to create a new table and
    the required columns columns needed for storing applications data.
    """
    db = get()

    reviewers = db.create_table("reviewers")
    reviewers.create_column("discord_id", db.types.bigint)

    applications = db.create_table("applications")
    applications.create_column("discord_id", db.types.bigint)
    applications.create_column("timestamp", db.types.bigint)
    applications.create_column("ip_address", db.types.bigint)
    applications.create_column("reddit_username", db.types.text)
    applications.create_column("referral", db.types.text)
    applications.create_column("about_me", db.types.text)
    applications.create_column("expectations", db.types.text)
    applications.create_column("already_known", db.types.text)
    applications.create_column("why_should_be_invited", db.types.text)
    applications.create_column("currently_watching", db.types.text)
    applications.create_column("favorite_anime", db.types.text)
    applications.create_column("do_you_have_a_list", db.types.text)
    applications.create_column("application_status", db.types.boolean)
    applications.create_column("reviewed_by", db.types.bigint)

    db.commit()
    db.close()


def check_if_app_exists(discord_id: int) -> bool:
    """
    Checks whether an application exists for the specified application
    and returns True or False accordingly.
    """
    db = get()
    entry = db["applications"].find_one(discord_id=discord_id)
    db.close()
    return True if entry else False


def insert_data_into_db(table: str, data: dict) -> None:
    """
    Inserts the data from a passed dictionary into the table.
    """
    db = get()
    db[table].insert(data)
    db.commit()
    db.close()


def get_stats() -> dict:
    """
    Iterates over the entire database to get statistics about the
    total, pending, accepted, and declined stats of the applications
    in the database.
    """
    db = get()
    results = list(db.query("SELECT * from applications"))
    stats = {"pending": 0, "total": len(results), "accepted": 0, "denied": 0}
    for row in results:
        if row["application_status"] is None:  # the app is pending.
            stats["pending"] += 1
        if row["application_status"]:  # the app is accepted.
            stats["accepted"] += 1
        if not row["application_status"]:  # the app is denied.
            stats["denied"] += 1
    return stats


def get_application(id) -> OrderedDict:
    """
    Returns the application data for the specified SQLite row ID.
    """
    db = get()
    result = db["applications"].find_one(id=id)
    db.close()
    return result


def get_reviewer(id) -> OrderedDict:
    """
    Returns the reviewer data for the specified Discord ID.
    """
    db = get()
    reviewer = db["reviewers"].find_one(discord_id=id)
    db.close()
    return reviewer if reviewer else None


def update_application_status(id: int, status: bool, reviewed_by: str) -> None:
    """
    Updates the status of the application with the new application
    status and the user#tag of who reviewed the application.
    """
    db = get()
    application = db["applications"].find_one(id=id)
    application["application_status"] = status
    application["reviewed_by"] = reviewed_by
    db["applications"].update(application, ["id"])
    db.commit()
    db.close()


def get_application_id_from_discord_id(id: int) -> Optional[int]:
    """
    Attempts to search for an application in the database by
    the Discord ID and returns the ID of the application found.
    """
    db = get()
    application = db["applications"].find_one(discord_id=id)
    db.close()
    return application["id"] if application else None


def get_application_id_from_ip(ip_address: str) -> Optional[int]:
    """
    Attempts to search for an application in the database by
    the IP address and returns the ID of the application found.
    """
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
