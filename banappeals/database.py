from collections import OrderedDict
from typing import Optional

import dataset
from dataset import Database


class Database:
    def get(self) -> Database:
        """
        Returns an active connection to the database.
        """
        return dataset.connect("sqlite:///config/data.db")

    def setup(self) -> None:
        """
        Connects to the database and attempts to create a new table and
        the required columns columns needed for storing applications data.
        """
        # Open a connection to the database.
        db = self.get()

        # Create the table that will hold the reviewers.
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

        # Commit the changes to the database and close the connection.
        db.commit()
        db.close()

    def check_if_app_exists(self, discord_id: int) -> bool:
        """
        Checks whether an application exists for the specified application
        and returns True or False accordingly.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Search for an application from the Discord ID.
        entry = table.find_one(discord_id=discord_id)

        # Close the connection to the database.
        db.close()

        # If we found an entry, return True.
        if entry:
            return True

        # Otherwise, no entry was found, return False.
        return False

    def insert_data_into_db(self, table: str, data: dict) -> None:
        """
        Inserts the data from a passed dictionary into the table.
        """
        # Open a connection to the database.
        db = self.get()
        table = db[table]

        # Inserts the application data into the database.
        table.insert(data)

        # Commit the changes to the database and close the connection.
        db.commit()
        db.close()

    def get_stats(self) -> dict:
        """
        Iterates over the entire database to get statistics about the
        total, pending, accepted, and declined stats of the applications
        in the database.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Query all the results from the table.
        results = db.query(f"SELECT * from {table.name}")
        data = []

        # Add all of the data from the table into the list.
        for row in results:
            data.append(row)

        # Create a dictionary for storing the stats data.
        stats = {
            "pending": 0,
            "total": len(data),
            "accepted": 0,
            "denied": 0
        }

        # Iterate over all the rows and add to the stats where appropriate
        for row in data:
            # If the application_status is null, the app is pending.
            if row["application_status"] is None:
                stats["pending"] += 1
            # If the application_status is True, the app is accepted.
            if row["application_status"]:
                stats["accepted"] += 1
            # If the application_status is False, the app is denied.
            if not row["application_status"]:
                stats["denied"] += 1

        return stats

    def get_application(self, id) -> OrderedDict:
        """
        Returns the application data for the specified SQLite row ID.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Find the result by the requested ID.
        result = table.find_one(id=id)

        # Close the connection to the database.
        db.close()

        # Return the application.
        return result

    def get_reviewer(self, id) -> OrderedDict:
        """
        Returns the reviewer data for the specified Discord ID.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["reviewers"]

        # Find the result by the requested ID.
        reviewer = table.find_one(discord_id=id)

        # If no reviewer with that ID existed, return None
        if not reviewer:
            return None

        # Close the connection to the database.
        db.close()

        # Return the application.
        return reviewer

    def update_application_status(self, id: int, status: bool, reviewed_by: str) -> None:
        """
        Updates the status of the application with the new application
        status and the user#tag of who reviewed the application.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Find the application in the database.
        application = table.find_one(id=id)

        # Update the rows for the application.
        application["application_status"] = status
        application["reviewed_by"] = reviewed_by
        table.update(application, ["id"])

        # Commit the changes to the database and close the connection.
        db.commit()
        db.close()

    def get_application_id_from_discord_id(self, id: int) -> Optional[int]:
        """
        Attempts to search for an application in the database by
        the Discord ID and returns the ID of the application found.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Find the application in the database.
        application = table.find_one(discord_id=id)

        # Close the connection to the database.
        db.close()

        # If no application with that ID existed, return None
        if not application:
            return None

        # Return the database ID for the Discord ID provided.
        return application["id"]

    def get_application_id_from_discord_user(self, username: str, discriminator: str) -> Optional[int]:
        """
        Attempts to search for an application in the database by
        the Discord ID and returns the ID of the application found.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Find the application in the database.
        application = table.find_one(username=username, discriminator=discriminator)

        # Close the connection to the database.
        db.close()

        # If no application with that ID existed, return None
        if not application:
            return None

        # Return the database ID for the Discord ID provided.
        return application["id"]

    def get_application_id_from_email(self, email: str) -> Optional[int]:
        """
        Attempts to search for an application in the database by
        the email address and returns the ID of the application found.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Find the application in the database.
        application = table.find_one(email_address=email)

        # Close the connection to the database.
        db.close()

        # If no application with that ID existed, return None
        if not application:
            return None

        # Return the database ID for the email provided.
        return application["id"]

    def get_application_id_from_ip(self, ip_address: str) -> Optional[int]:
        """
        Attempts to search for an application in the database by
        the IP address and returns the ID of the application found.
        """
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Find the application in the database.
        application = table.find_one(ip_address=ip_address)

        # Close the connection to the database.
        db.close()

        # If no application with that ID existed, return None
        if not application:
            return None

        # Return the database ID for the email provided.
        return application["id"]

    def get_oldest_pending_application(self) -> Optional[dict]:
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Find the first application in the database.
        application = table.find_one(application_status=None)

        # Close the connection to the database.
        db.close()

        # If no pending applications exist, return None
        if not application:
            return None

        return application

    def get_surrounding_applications(self, id) -> tuple:
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Attempt to grab the surrounding entries in the database..
        before = next(table.find(id={"<": id}, application_status=None, order_by="-id", _limit=1), None)
        after = next(table.find(id={">": id}, application_status=None, _limit=1), None)

        # Close the connection to the database.
        db.close()

        # Return the two applications as a tuple.
        return ((before, after))

    def get_all_applications(self):
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Get all of the rows in the database.
        results = db.query(f"SELECT * from {table.name}")
        data = []
        for row in results:
            data.append(row)

        # Close the connection to the database.
        db.close()

        # Return all of the rows from the database.
        return data

    def get_reviewed_applications(self):
        # Open a connection to the database.
        db = self.get()
        table = db["applications"]

        # Get all of the rows in the database.
        results = table.find(application_status={"not": None})

        data = []
        for row in results:
            data.append(row)

        # Close the connection to the database.
        db.close()

        # Return all of the rows from the database.
        return data
