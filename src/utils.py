from datetime import datetime
import discord
from discord.ext import commands


def dt_to_timestamp(dt: datetime, f: str = None) -> str:
    """Converts a datetime object to a Discord timestamp.

    Args:
        dt (datetime): The datetime object to convert.
        format (str): The format that the timestamp should be in. See the Discord Developer Documentation for more info: https://discord.com/developers/docs/reference#message-formatting-timestamp-styles

    Returns:
        str: The timestamp.
    """
    formats = ["d", "D", "t", "T", "f", "F", "R"]
    if f not in formats:
        return str(int(dt.timestamp()))
    else:
        return f"<t:{int(dt.timestamp())}:{f}>"


def epoch_to_datetime(epoch_time: str):
    if epoch_time.isnumeric():
        epoch_time = int(epoch_time)

        return datetime.fromtimestamp(epoch_time)
    else:
        raise Exception("Timestamp must be numeric.")


def format_interaction_msg(s: str, interaction: discord.Interaction):
    return (
        s.replace("{user_mention}", interaction.user.mention)
        .replace("{user_name}", interaction.user.name)
        .replace("{user_id}", str(interaction.user.id))
    )


def format_ctx_msg(s: str, ctx: commands.Context):
    return (
        s.replace("{user_mention}", ctx.author.mention)
        .replace("{user_name}", ctx.author.name)
        .replace("{user_id}", str(ctx.author.id))
    )
