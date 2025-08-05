import config
from supabase import create_client
from playhouse.postgres_ext import *
from peewee import *
from enum import Enum
from datetime import datetime
from datetime import timezone

# deprecated, use psql_db instead
supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


psql_db = PostgresqlExtDatabase(
    "fansbot", user=config.DATABASE_USER, password=config.DATABASE_PASSWORD
)


class ModerationCaseType(Enum):
    OTHER = "OTHER"
    NOTE = "NOTE"
    WARN = "WARN"
    MUTE = "MUTE"
    KICK = "KICK"
    BAN = "BAN"


class ModerationCaseStatus(Enum):
    OTHER = "OTHER"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class GlossaryTermType(Enum):
    OTHER = "OTHER"
    ACRONYM = "ACRONYM"
    TERM = "TERM"
    EMOJI = "EMOJI"


class PredictionStatus(Enum):
    EXISTS = "EXISTS"
    POSTED = "POSTED"
    VOTING = "VOTING"
    AWAITING_RESULTS = "AWAITING_RESULTS"
    COMPLETE = "COMPLETE"


class PredictionPrizeType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    POT = "POT"


class EnumField(CharField):
    def __init__(self, enum: type[Enum], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum = enum

    def db_value(self, value):
        if value is None:
            return None
        return value.value

    def python_value(self, value):
        if value is None:
            return None
        return self.enum(value)


class ModerationCase(Model):
    user_id = TextField(null=False)
    case_type = EnumField(ModerationCaseType, null=False)
    message = TextField(null=False)
    proof = ArrayField(TextField, null=True)
    created_by = TextField(null=False)
    created_at = DateTimeTZField(null=False, default=datetime.now(timezone.utc))
    rules = ArrayField(IntegerField, null=True)
    expires_at = DateTimeTZField(null=True)
    status = EnumField(
        ModerationCaseStatus, null=False, default=ModerationCaseStatus.OPEN
    )
    editors = ArrayField(TextField, null=False)
    last_edited = DateTimeTZField(null=False, default=datetime.now(timezone.utc))
    history = JSONField(null=True)

    @staticmethod
    def split_string(obj: str):
        return obj.split("\\")

    class Meta:
        database = psql_db


class GlossaryTerm(Model):
    created_at = DateTimeTZField(null=False, default=datetime.now(timezone.utc))
    created_by = TextField(null=False)
    title = TextField(null=False)
    description = TextField(null=False)
    term_type = EnumField(GlossaryTermType, null=False, default=GlossaryTermType.OTHER)
    last_updated = DateTimeTZField(null=False, default=datetime.now(timezone.utc))
    editors = ArrayField(TextField, null=False)

    class Meta:
        database = psql_db


class Predictions(Model):
    created_at = DateTimeTZField(null=False, default=datetime.now(timezone.utc))
    created_by = TextField(null=False)
    ends_at = DateTimeTZField(null=False)
    title = TextField(null=False)
    options = JSONField(null=False)  # and participants
    prize_amount = IntegerField(null=True)
    channel_id = TextField(null=False)
    message_id = TextField(null=False)
    prizetype = EnumField(
        PredictionPrizeType, null=False, default=PredictionPrizeType.INDIVIDUAL
    )
    status = EnumField(PredictionStatus, null=False, default=PredictionStatus.EXISTS)

    class Meta:
        database = psql_db


class AutoPredictions(Model):
    created_at = DateTimeTZField(null=False, default=datetime.now(timezone.utc))
    time = TimeField(null=False)
    monday = BooleanField(null=False, default=True)
    tuesday = BooleanField(null=False, default=True)
    wednesday = BooleanField(null=False, default=True)
    thursday = BooleanField(null=False, default=True)
    friday = BooleanField(null=False, default=True)
    saturday = BooleanField(null=False, default=True)
    sunday = BooleanField(null=False, default=True)
    end_on = DateField(null=True)
    duration = JSONField(null=False)
    title = TextField(null=False)
    options = ArrayField(TextField, null=False)
    prize_amount = IntegerField(null=False)
    channel_id = TextField(null=False)
    prizetype = EnumField(
        PredictionPrizeType, null=False, default=PredictionPrizeType.INDIVIDUAL
    )
    enabled = BooleanField(null=False, default=True)

    class Meta:
        database = psql_db
