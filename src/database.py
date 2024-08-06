import peewee

db = peewee.SqliteDatabase("src/data/database.db")


class ModerationNote(peewee.Model):
    user_id: int = peewee.IntegerField(null=False)
    content: str = peewee.CharField(null=False)
    proof: str = peewee.CharField(null=True)
    created_by: int = peewee.IntegerField(null=False)
    created_at: int = peewee.IntegerField(null=False)
    rule: int = peewee.IntegerField(null=True)

    class Meta:
        database = db


class ModerationWarning(peewee.Model):
    user_id: int = peewee.IntegerField(null=False)
    content: str = peewee.CharField(null=False)
    proof: str = peewee.CharField(null=True)
    created_by: int = peewee.IntegerField(null=False)
    created_at: int = peewee.IntegerField(null=False)
    rule: int = peewee.IntegerField(null=True)

    class Meta:
        database = db


class ModerationMute(peewee.Model):
    user_id: int = peewee.IntegerField(null=False)
    content: str = peewee.CharField(null=False)
    proof: str = peewee.CharField(null=True)
    created_by: int = peewee.IntegerField(null=False)
    created_at: int = peewee.IntegerField(null=False)
    rule: int = peewee.IntegerField(null=True)

    class Meta:
        database = db


class ModerationKick(peewee.Model):
    user_id: int = peewee.IntegerField(null=False)
    content: str = peewee.CharField(null=False)
    proof: str = peewee.CharField(null=True)
    created_by: int = peewee.IntegerField(null=False)
    created_at: int = peewee.IntegerField(null=False)
    rule: int = peewee.IntegerField(null=True)

    class Meta:
        database = db


class ModerationBan(peewee.Model):
    user_id: int = peewee.IntegerField(null=False)
    content: str = peewee.CharField(null=False)
    proof: str = peewee.CharField(null=True)
    created_by: int = peewee.IntegerField(null=False)
    created_at: int = peewee.IntegerField(null=False)
    rule: int = peewee.IntegerField(null=True)

    class Meta:
        database = db
