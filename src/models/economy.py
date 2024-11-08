import peewee
import database


class Economy(peewee.Model):
    user_id: int = peewee.IntegerField(unique=True, null=False)
    cash: int = peewee.IntegerField(default=0, null=False)
    has_bank_account: bool = peewee.BooleanField(default=False, null=False)
    bank: int = peewee.IntegerField(default=0, null=False)
    income: str = peewee.CharField(default=str({}), null=False)  # stringified dict
    items: str = peewee.CharField(default=str({}), null=False)  # stringified dict

    @staticmethod
    def fetch(user: int):
        try:
            return Economy.create(user_id=user)
        except peewee.IntegrityError:
            return Economy.get(Economy.user_id == user)

    class Meta:
        database = database.db


class WorkReplies(peewee.Model):
    text: str = peewee.CharField(null=False)

    @staticmethod
    def get_all():
        return WorkReplies.select()

    class Meta:
        database = database.db
