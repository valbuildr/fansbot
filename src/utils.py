from datetime import datetime


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
