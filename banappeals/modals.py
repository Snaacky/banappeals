from banappeals import database


class Appeal:
    def __init__(
        self,
        discord_user: str,
        discord_id: int,
        ban_reason: str,
        ban_explanation: str,
        unban_explantion: str,
        additional_comments: str,
        status: bool,
        reviewer: str,
        timestamp: int,
        ip_address: str,
    ) -> None:
        self.discord_user = discord_user
        self.discord_id = discord_id
        self.ban_reason = ban_reason
        self.ban_explanation = ban_explanation
        self.unban_explantion = unban_explantion
        self.additional_comments = additional_comments
        self.status = status
        self.reviewer = reviewer
        self.timestamp = timestamp
        self.ip_address = ip_address

    def save(self):
        db = database.get()
        db["appeals"].insert(vars(self))
        db.commit()
        db.close()

    def approve(self, reviewer: int):
        db = database.get()
        appeal = db["appeals"].find_one(id=id)
        appeal["status"] = True
        appeal["reviewer"] = reviewer
        appeal.update(appeal, ["id"])
        db.commit()
        db.close()

    def reject(self, reviewer: int):
        db = database.get()
        appeal = db["appeals"].find_one(id=id)
        appeal["status"] = False
        appeal["reviewer"] = reviewer
        appeal.update(appeal, ["id"])
        db.commit()
        db.close()
