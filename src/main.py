import time
import discord
import os
import config
from discord.ext import commands
from discord.ext import tasks
from random import choice
import database
import requests
from datetime import datetime
from datetime import timezone
import git
import utils
from logging import getLogger
from discord import ui
from discord import app_commands as appcmds
import json

log = getLogger("discord.fansbot")

bot = commands.Bot(command_prefix="~", intents=discord.Intents.all())


if not os.path.exists("src/data"):
    os.makedirs("src/data")
if not os.path.exists("src/static"):
    os.makedirs("src/static")


@tasks.loop(seconds=120)
async def change_status():
    statuses = [
        discord.Activity(type=discord.ActivityType.watching, name="BBC One"),
        discord.Activity(type=discord.ActivityType.watching, name="BBC Two"),
        discord.Activity(type=discord.ActivityType.watching, name="BBC Three"),
        discord.Activity(type=discord.ActivityType.watching, name="BBC Four"),
        discord.Activity(type=discord.ActivityType.watching, name="BBC News"),
        discord.Activity(type=discord.ActivityType.watching, name="BBC Scotland"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 1"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 1 Xtra"),
        discord.Activity(
            type=discord.ActivityType.listening, name="BBC Radio 1 Anthems"
        ),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 1 Dance"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 2"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 3"),
        discord.Activity(
            type=discord.ActivityType.listening, name="BBC Radio 3 Unwind"
        ),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 4"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 4 Extra"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 5 Live"),
        discord.Activity(
            type=discord.ActivityType.listening, name="BBC Radio 5 Sports Extra"
        ),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Radio 6 Music"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Asian Network"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC World Service"),
        discord.Activity(type=discord.ActivityType.listening, name="BBC Live News"),
        discord.CustomActivity(name="Keeping up with the BBC"),
        discord.CustomActivity(name="beep boop beep"),
        discord.CustomActivity(name="Now hosted entirely in the UK!"),
        discord.CustomActivity(name="i use arch btw"),
    ]

    chosen = choice(statuses)

    await bot.change_presence(activity=chosen)


@tasks.loop(hours=1)
async def auto_move_specials():
    guild = bot.get_guild(config.SERVER_ID)

    channel = guild.get_channel(config.SPECIALS_CHANNEL_ID)
    if channel.type == discord.ChannelType.forum:
        tags = channel.available_tags
        archive_tag = None
        for tag in tags:
            if tag.name == config.SPECIALS_ARCHIVE_TAG_NAME:
                archive_tag = tag

        active_post = False

        for post in channel.threads:
            if (
                archive_tag not in post.applied_tags
                and post.archived == False
                and post.locked == False
            ):
                active_post = True

        main_cat = guild.get_channel(config.MAIN_CATEGORY_ID)
        other_cat = guild.get_channel(config.OTHER_CATEGORY_ID)

        if active_post:
            await channel.move(beginning=True, offset=1, category=main_cat)
        else:
            await channel.move(end=True, category=other_cat)


@tasks.loop(hours=24)
async def keep_supabase_alive():
    # query supabase just so it doesnt archive
    data = database.supabase_client.table("keep_alive").select("*").execute()


services = {
    "18048": {
        "name": "BBC Four",
        "region": None,
        "banner": "four.png",
        "bbc": "https://www.bbc.co.uk/schedules/p01kv81d",
        "type": "tv",
    },
    "17920": {
        "name": "BBC Three",
        "region": None,
        "banner": "three.png",
        "bbc": "https://www.bbc.co.uk/schedules/p01kv7xf",
        "type": "tv",
    },
    "17472": {
        "name": "BBC Two",
        "region": None,
        "banner": "two.png",
        "bbc": "https://www.bbc.co.uk/schedules/p015pksy",
        "type": "tv",
    },
    "17536": {
        "name": "BBC One",
        "region": "London",
        "banner": "one.png",
        "bbc": "https://www.bbc.co.uk/schedules/p00fzl6p",
        "type": "tv",
    },
    "4352": {
        "name": "BBC News",
        "region": "UK",
        "banner": "news.png",
        "bbc": "https://www.bbc.co.uk/schedules/p00fzl6g",
        "type": "tv",
    },
    "6912": {
        "name": "BBC Radio 4",
        "region": None,
        "banner": "4.png",
        "bbc": "https://www.bbc.co.uk/schedules/p00fzl7j",
        "type": "radio",
    },
    "5632": {
        "name": "BBC Radio 5 Live",
        "region": None,
        "banner": "5.png",
        "bbc": "https://www.bbc.co.uk/schedules/p00fzl7g",
        "type": "radio",
    },
    "6016": {
        "name": "BBC World Service",
        "region": "UK DAB/Freeview",
        "banner": "worldservice.png",
        "bbc": "https://www.bbc.co.uk/schedules/p02zbmb3",
        "type": "radio",
    },
}


def format_schedule(
    banner_name: str,
    channel_name: str,
    events: list,
    bbc_schedule_url: str,
    channel_region: str | None = None,
):
    now = datetime.now(timezone.utc)

    view = ui.LayoutView()
    container = ui.Container()
    container.add_item(
        ui.MediaGallery(discord.MediaGalleryItem(f"attachment://{banner_name}"))
    )
    if channel_region:
        container.add_item(
            ui.TextDisplay(f"# {channel_name} [{channel_region}] Schedule")
        )
    else:
        container.add_item(ui.TextDisplay(f"# {channel_name} Schedule"))
    events_text = ""
    # Find the index of the current event
    current_index = None
    for i, event in enumerate(events):
        event_start = datetime.fromisoformat(event["start_time"])
        if event_start <= now:
            if (
                i + 1 >= len(events)
                or datetime.fromisoformat(events[i + 1]["start_time"]) > now
            ):
                current_index = i
    if current_index is None:
        current_index = 0  # fallback if no current event found

    # Calculate the window of events to display
    start_idx = max(0, current_index - 3)
    end_idx = min(len(events), current_index + 1 + 10)  # +1 to include current event

    for i in range(start_idx, end_idx):
        event = events[i]
        event_start = datetime.fromisoformat(event["start_time"])
        if i == current_index:
            events_text += f":arrow_right: **{utils.dt_to_timestamp(event_start, 't')} [{event['main_title']}](https://bbc.co.uk/programmes/{event['program_id'].split('/')[-1]})**\n"
        else:
            events_text += f":black_large_square: {utils.dt_to_timestamp(event_start, 't')} [{event['main_title']}](https://bbc.co.uk/programmes/{event['program_id'].split('/')[-1]})\n"
    container.add_item(ui.TextDisplay(events_text))
    container.add_item(ui.Separator())
    container.add_item(
        ui.TextDisplay(f"-# Last updated: {utils.dt_to_timestamp(datetime.now(), 'f')}")
    )
    container.add_item(
        ui.Section(
            ui.TextDisplay("Full schedule:"),
            accessory=ui.Button(url=bbc_schedule_url, label="Open"),
        )
    )
    container.add_item(ui.Separator())
    container.add_item(
        ui.TextDisplay(
            "-# **This feature is in beta!** Please report any bugs to valbuilded."
        )
    )
    view.add_item(container)

    return view


@tasks.loop(minutes=15)
async def update_scheules():
    now = datetime.now(timezone.utc)
    midnight_utc = now.replace(hour=0, minute=0, second=0, microsecond=0)

    request = requests.get(
        "https://www.freeview.co.uk/api/tv-guide",
        params={"nid": "64257", "start": utils.dt_to_timestamp(midnight_utc, "a")},
    )

    data = request.json()

    # Iterate over services in the order defined in the 'services' dict
    for service_id in services.keys():
        # Find the matching service data from the API response
        service = next(
            (s for s in data["data"]["programs"] if s["service_id"] == service_id), None
        )
        if not service:
            continue

        view = format_schedule(
            services[service_id]["banner"],
            services[service_id]["name"],
            service["events"],
            services[service_id]["bbc"],
            services[service_id]["region"],
        )

        if os.path.exists(f"src/data/{service_id}.json"):
            file = json.load(open(f"src/data/{service_id}.json", "r"))
        else:
            json.dump(
                {"event": service["events"]}, open(f"src/data/{service_id}.json", "w")
            )
            file = open(f"src/data/{service_id}.json", "r").read()

        if file != {"event": service["events"]}:
            if os.path.exists(f"src/data/{service_id}.txt"):
                # Open file (r)
                f = open(f"src/data/{service_id}.txt", "r")
                # Find message
                if services[service_id]["type"] == "radio":
                    channel = (
                        bot.get_guild(config.SERVER_ID)
                        .get_channel(config.SCHEDULES_CHANNEL_ID)
                        .get_thread(config.RADIO_SCHEDULES_THREAD_ID)
                    )
                else:
                    channel = bot.get_guild(config.SERVER_ID).get_channel(
                        config.SCHEDULES_CHANNEL_ID
                    )
                try:
                    message = await channel.fetch_message(f.read())
                except:
                    message = None
                if message:
                    # If message found: Edit message
                    await message.edit(
                        view=view,
                    )
                else:
                    # Else: Create message
                    msg = await channel.send(
                        view=view,
                        files=[
                            discord.File(
                                f"src/static/schedule-banners/{services[service_id]['banner']}"
                            )
                        ],
                    )
                    # Else: Open file (w)
                    f = open(f"src/data/{service_id}.txt", "w")
                    # Else: Write message id to file
                    f.write(str(msg.id))
            else:
                # Open file (w)
                f = open(f"src/data/{service_id}.txt", "w")
                # Create message
                if services[service_id]["type"] == "radio":
                    channel = (
                        bot.get_guild(config.SERVER_ID)
                        .get_channel(config.SCHEDULES_CHANNEL_ID)
                        .get_thread(config.RADIO_SCHEDULES_THREAD_ID)
                    )
                else:
                    channel = bot.get_guild(config.SERVER_ID).get_channel(
                        config.SCHEDULES_CHANNEL_ID
                    )
                msg = await channel.send(
                    view=view,
                    files=[
                        discord.File(
                            f"src/static/schedule-banners/{services[service_id]['banner']}"
                        )
                    ],
                )
                # Write message id to file
                f.write(str(msg.id))


tv_regions = {
    "64334": {
        "name": "Channel Islands",
        "one": ["17550", "https://www.bbc.co.uk/schedules/p00fzl6j", "Channel Islands"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64304": {
        "name": "East",
        "one": ["17543", "https://www.bbc.co.uk/schedules/p00fzl6k", "East"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64345": {
        "name": "East Midlands",
        "one": ["17542", "https://www.bbc.co.uk/schedules/p00fzl6l", "East Midlands"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64257": {
        "name": "London",
        "one": ["17536", "https://www.bbc.co.uk/schedules/p00fzl6p", "London"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64369": {
        "name": "North East & Cumbria",
        "one": [
            "17545",
            "https://www.bbc.co.uk/schedules/p00fzl6r",
            "North East & Cumbria",
        ],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64369": {
        "name": "North West",
        "one": ["17544", "https://www.bbc.co.uk/schedules/p00fzl6s", "North West"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64425": {
        "name": "Northern Ireland",
        "one": [
            "17597",
            "https://www.bbc.co.uk/schedules/p00zskxc",
            "Northern Ireland",
        ],
        "two": [
            "17533",
            "https://www.bbc.co.uk/schedules/p06ngcbm",
            "Northern Ireland",
        ],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64405": {
        "name": "Scotland",
        "one": ["17596", "https://www.bbc.co.uk/schedules/p013blmc", "Scotland"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", "Scotland"],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64273": {
        "name": "South",
        "one": ["17539", "https://www.bbc.co.uk/schedules/p00fzl6w", "South"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64280": {
        "name": "South East",
        "one": ["17548", "https://www.bbc.co.uk/schedules/p00fzl6x", "South East"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64328": {
        "name": "South West",
        "one": ["17538", "https://www.bbc.co.uk/schedules/p00fzl6y", "South West"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64417": {
        "name": "Wales",
        "one": ["17598", "https://www.bbc.co.uk/schedules/p013bkc7", "Wales"],
        "two": ["17534", "https://www.bbc.co.uk/schedules/p06ngc52", "Wales"],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64321": {
        "name": "West",
        "one": ["17537", "https://www.bbc.co.uk/schedules/p00fzl70", "West"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64337": {
        "name": "West Midlands",
        "one": ["17541", "https://www.bbc.co.uk/schedules/p00fzl71", "West Midlands"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64353": {
        "name": "Yorkshire & Lincolnshire",
        "one": [
            "64353",
            "https://www.bbc.co.uk/schedules/p00fzl6m",
            "Yorkshire & Lincolnshire",
        ],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
    "64363": {
        "name": "Yorkshire",
        "one": ["17546", "https://www.bbc.co.uk/schedules/p00fzl72", "East"],
        "two": ["17472", "https://www.bbc.co.uk/schedules/p015pksy", None],
        "three": ["17920", "https://www.bbc.co.uk/schedules/p01kv7xf", None],
        "four": ["18048", "https://www.bbc.co.uk/schedules/p01kv81d", None],
        "cbbc": ["18112", "https://www.bbc.co.uk/schedules/p01kv86b", None],
        "cbeebies": ["18176", "https://www.bbc.co.uk/schedules/p01kv8yz", None],
        "news": ["4352", "https://www.bbc.co.uk/schedules/p00fzl6g", "UK"],
        "parliament": ["4736", "https://www.bbc.co.uk/schedules/p00fzl73", None],
    },
}


national_radios = {
    "6720": {
        "name": "BBC Radio 1",
        "region": None,
        "banner": "1.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl86",
    },
    "5888": {
        "name": "BBC Radio 1 Xtra",
        "region": None,
        "banner": "1x.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl64",
    },
    "6784": {
        "name": "BBC Radio 2",
        "region": None,
        "banner": "2.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl8v",
    },
    "6848": {
        "name": "BBC Radio 3",
        "region": None,
        "banner": "3.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl8t",
    },
    "6912": {
        "name": "BBC Radio 4",
        "region": None,
        "banner": "4.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl7j",
    },
    "5632": {
        "name": "BBC Radio 5 Live",
        "region": None,
        "banner": "5.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl7g",
    },
    "5696": {
        "name": "BBC Radio 5 Sports Extra",
        "region": None,
        "banner": "5x.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl7h",
    },
    "5760": {
        "name": "BBC Radio 6 Music",
        "region": None,
        "banner": "6.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl65",
    },
    "5824": {
        "name": "BBC Radio 4 Extra",
        "region": None,
        "banner": "4x.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl7l",
    },
    "5952": {
        "name": "BBC Asian Network",
        "region": None,
        "banner": "asian.png",
        "schedule": "https://www.bbc.co.uk/schedules/p00fzl68",
    },
    "6016": {
        "name": "BBC World Service",
        "region": "UK DAB/Freeview",
        "banner": "worldservice.png",
        "schedule": "https://www.bbc.co.uk/schedules/p02zbmb3",
    },
}


async def tv_region_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[appcmds.Choice[str]]:
    return [
        appcmds.Choice(name=region["name"], value=region_id)
        for region_id, region in tv_regions.items()
        if current.lower() in region["name"].lower()
    ]


async def radio_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[appcmds.Choice[str]]:
    return [
        appcmds.Choice(name=network["name"], value=network_id)
        for network_id, network in national_radios.items()
        if current.lower() in network["name"].lower()
    ]


class ScheduleCommands(appcmds.Group):
    @appcmds.command(name="tv", description="Get the schedule for a BBC TV service.")
    @appcmds.choices(
        channel=[
            appcmds.Choice(name="BBC One HD", value="one"),
            appcmds.Choice(name="BBC Two HD", value="two"),
            appcmds.Choice(name="BBC Three HD", value="three"),
            appcmds.Choice(name="BBC Four HD", value="four"),
            appcmds.Choice(name="CBBC HD", value="cbbc"),
            appcmds.Choice(name="CBeebies HD", value="cbeebies"),
            appcmds.Choice(name="BBC News", value="news"),
            appcmds.Choice(name="BBC Parliament", value="parliament"),
        ]
    )
    @appcmds.autocomplete(region=tv_region_autocomplete)
    async def tv(
        self, interaction: discord.Interaction, channel: str, region: str = "64257"
    ):
        await interaction.response.defer(ephemeral=True)

        now = datetime.now(timezone.utc)
        midnight_utc = now.replace(hour=0, minute=0, second=0, microsecond=0)

        request = requests.get(
            "https://www.freeview.co.uk/api/tv-guide",
            params={"nid": region, "start": utils.dt_to_timestamp(midnight_utc, "a")},
        )

        data = request.json()

        # Default to London
        if region not in tv_regions.keys():
            region = "64257"

        meta = tv_regions[region]

        service = next(
            (
                s
                for s in data["data"]["programs"]
                if s["service_id"] == meta[channel][0]
            ),
            None,
        )

        channel_names = {
            "one": "BBC One",
            "two": "BBC Two",
            "three": "BBC Three",
            "four": "BBC Four",
            "cbbc": "CBBC",
            "cbeebies": "Cbeebies",
            "news": "BBC News",
            "parliament": "BBC Parliament",
        }

        view = format_schedule(
            f"{channel}.png",
            channel_names[channel],
            service["events"],
            meta[channel][1],
            meta[channel][2],
        )

        await interaction.followup.send(
            view=view,
            files=[discord.File(f"src/static/schedule-banners/{channel}.png")],
        )

    @appcmds.command(
        name="national-radio",
        description="Get the schedule for a national BBC Radio service.",
    )
    @appcmds.autocomplete(network=radio_autocomplete)
    async def radio(self, interaction: discord.Interaction, network: str):
        await interaction.response.defer(ephemeral=True)

        now = datetime.now(timezone.utc)
        midnight_utc = now.replace(hour=0, minute=0, second=0, microsecond=0)

        request = requests.get(
            "https://www.freeview.co.uk/api/tv-guide",
            params={"nid": "64257", "start": utils.dt_to_timestamp(midnight_utc, "a")},
        )

        data = request.json()

        # Default to World Service
        if network not in national_radios.keys():
            network = "6016"

        meta = national_radios[network]

        service = next(
            (s for s in data["data"]["programs"] if s["service_id"] == network)
        )

        view = format_schedule(
            meta["banner"],
            meta["name"],
            service["events"],
            meta["schedule"],
            meta["region"],
        )

        await interaction.followup.send(
            view=view,
            files=[discord.File(f"src/static/schedule-banners/{meta['banner']}")],
        )


@bot.event
async def on_ready() -> None:
    change_status.start()
    auto_move_specials.start()
    keep_supabase_alive.start()
    update_scheules.start()

    await bot.load_extension("ext.tickets")
    await bot.load_extension("ext.moderation")
    await bot.load_extension("ext.games")

    bot.tree.add_command(
        ScheduleCommands(name="schedule", description="Schedule commands")
    )

    log.info(f"Logged in as {bot.user.name}")


@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == config.SERVER_ID:
        await member.add_roles(discord.Object(id=config.unverified_role_id))

        welcome_channel = bot.get_guild(config.SERVER_ID).get_channel(
            config.NEW_MEMBERS_CHANNEL_ID
        )

        welcome_view = discord.ui.LayoutView()
        welcome_view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    f"Welcome {member.mention}! Please read through our <#{config.RULES_CHANNEL_ID}> and click the 'I agree' button to gain full access to the server.\n-# Joined Discord: {utils.dt_to_timestamp(member.created_at, "D")} ({utils.dt_to_timestamp(member.created_at, "R")})\n-# ID: {member.id}"
                ),
                accent_color=discord.Color.green()
            )
        )

        await welcome_channel.send(
            view=welcome_view
        )


@bot.event
async def on_member_remove(member: discord.Member):
    if member.guild.id == config.SERVER_ID:
        welcome_channel = bot.get_guild(config.SERVER_ID).get_channel(
            config.NEW_MEMBERS_CHANNEL_ID
        )

        welcome_view = discord.ui.LayoutView()
        welcome_view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    f"{member.name} has left.\n-# ID: {member.id}\n-# Joined: {utils.dt_to_timestamp(member.joined_at, "R")}]"
                ),
                accent_color=discord.Color.red()
            )
        )

        await welcome_channel.send(
            view=welcome_view
        )


@bot.event
async def on_thread_update(before: discord.Thread, after: discord.Thread):
    if before.locked == False and after.locked == True:
        if after.parent.id in [config.MOCKS_CHANNEL_ID, config.OTHER_CATEGORY_ID]:
            e = discord.Embed(
                title="This post has been locked by a moderator.",
                color=discord.Color.blue(),
            )
            e.add_field(
                name="Moderator Note",
                value="*A moderator has not yet added a note onto this closure.*\n-# If you are a moderator and would like to add a note, just reply to this message and I'll add it here.",
            )
            e.timestamp = datetime.now()
            match after.parent.id:
                case config.MOCKS_CHANNEL_ID:
                    e.description = "Common reasons for this action in this channel are:\n- This mock does not meet the effort requirement.\n- This mock is not mady by the poster, and was credit was not properly given to the original creator."
                case config.OTHER_TV_CHANNEL_ID:
                    e.description = "Common reasons for this action in this channel are:\n- A simillar post already exists."

            await after.send(embed=e)


@bot.event
async def on_message(message: discord.Message):
    if message.channel.id == config.polls_channel_id and message.poll != None:
        await message.create_thread(name=message.poll.question)

    if (
        message.channel.type == discord.ChannelType.public_thread
        and message.channel.parent.id
        in [config.MOCKS_CHANNEL_ID, config.OTHER_CATEGORY_ID]
        and bot.get_guild(config.GUILD_ID).get_role(config.MOD_ROLE_ID)
        in message.author.roles
        and message.channel.locked
        and message.type == discord.MessageType.reply
    ):
        await message.add_reaction("🔍")
        lock_msg = await message.channel.fetch_message(message.reference.message_id)
        if (
            lock_msg.author == bot.user
            and len(lock_msg.embeds) == 1
            and lock_msg.embeds[0].title == "This post has been locked by a moderator."
        ):
            e = lock_msg.embeds[0]
            new_embed = discord.Embed(
                title=e.title,
                description=e.description,
                color=e.color,
                timestamp=e.timestamp,
            )
            new_embed.add_field(
                name=e.fields[0].name,
                value=f"> {message.content} \n\\- {message.author.mention} {utils.dt_to_timestamp(message.created_at, 'f')}",
            )
            print(new_embed.fields[0].value)

            await lock_msg.edit(embed=new_embed)

            await message.remove_reaction("🔍", bot.user)
            await message.add_reaction("✅")
        else:
            await message.remove_reaction("🔍", bot.user)
            await message.add_reaction("❌")

    await bot.process_commands(message)


@bot.event
async def on_interaction(interaction: discord.Interaction) -> None:
    if interaction.type == discord.InteractionType.component:
        if (
            interaction.data["custom_id"] == "agree_to_rules"
            and interaction.data["component_type"] == 2
        ):
            member_role = bot.get_guild(config.server_id).get_role(
                config.member_role_id
            )
            if member_role not in interaction.user.roles:
                await interaction.user.add_roles(
                    discord.Object(id=config.member_role_id)
                )
                await interaction.user.remove_roles(
                    discord.Object(id=config.unverified_role_id)
                )

                await interaction.response.send_message(
                    content="Thanks for agreeing to the rules, I've added the member role to your profile.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    content="You already have the member role, so I haven't done anything.",
                    ephemeral=True,
                )
        elif (
            interaction.data["custom_id"] == "appeal_warnings"
            and interaction.data["component_type"] == 2
        ):
            e = discord.Embed(
                title="How to appeal warnings",
                description="To appeal a warning, simply open a ticket.\n In https://discord.com/channels/1016626731785928715/1097533655682912416, run `/ticket create` and a staff member will be with you shortly.",
                color=discord.Color.blue(),
            )
            await interaction.response.send_message(embed=e)
        elif (
            interaction.data["custom_id"] == "appeal_mutes"
            and interaction.data["component_type"] == 2
        ):
            e = discord.Embed(
                title="How to appeal mutes",
                description="To appeal a mute, open a ticket after your mute expires.\n After your mute expires, go to https://discord.com/channels/1016626731785928715/1097533655682912416 and run `/ticket create`. A staff member will be with you shortly.\n-# A way to appeal active mutes is in the works.",
                color=discord.Color.blue(),
            )
            await interaction.response.send_message(embed=e)
        elif (
            interaction.data["custom_id"] == "appeal_kicks"
            and interaction.data["component_type"] == 2
        ):
            e = discord.Embed(
                title="How to appeal kicks",
                description="To appeal a kick, open a ticket after you rejoin the server.\n After you rejoin the server, go to https://discord.com/channels/1016626731785928715/1097533655682912416 and run `/ticket create`. A staff member will be with you shortly.",
                color=discord.Color.blue(),
            )
            await interaction.response.send_message(embed=e)


@bot.command(hidden=True)
@commands.guild_only()
async def rules_channel_msg(ctx: commands.Context) -> None:
    channel = bot.get_guild(config.server_id).get_channel(config.rules_channel_id)
    mod_role = bot.get_guild(config.server_id).get_role(config.mod_role_id)

    if mod_role in ctx.author.roles:
        v = discord.ui.View(timeout=None)
        b = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="I agree to the rules listed above.",
            custom_id="agree_to_rules",
        )
        v.add_item(b)

        rules = open("./src/data/rules.txt", "r").read()
        receive_member_role = open("./src/data/receive_member_role.txt", "r").read()

        m = await channel.send(view=v)

        time.sleep(2)

        await m.edit(content=rules + "\n\n" + receive_member_role, view=v)


@bot.command()
@commands.is_owner()
@commands.dm_only()
async def sync(ctx: commands.Context) -> None:
    r = await ctx.send(content="Syncing...")
    await bot.tree.sync()
    await r.edit(content="Synced!")


@bot.tree.command(name="rules", description="Gets the server rules!")
@appcmds.guild_only()
async def rules(interaction: discord.Interaction) -> None:
    f = open("./src/data/rules.txt", "r")
    rules = f.read()

    await interaction.response.send_message(content=rules, ephemeral=True)
    f.close()


@bot.tree.command(
    name="messages",
    description="Mod: Gets the conversation between the bot and a user.",
)
@appcmds.describe(user="The user.")
async def messages(interaction: discord.Interaction, user: discord.User):
    await user.create_dm()
    if user.dm_channel:
        await interaction.response.defer()
        L = 5
        messages = [message async for message in user.history(limit=200)]
        print(messages)

        # create pagination
        async def get_page(page: int):
            emb = discord.Embed(
                title=f"Messages with {user.name}", colour=discord.Color.blue()
            )
            offset = (page - 1) * L

            for item in messages[offset : offset + L]:
                content = item.content.replace("\n", "\n> ")
                if len(content) > 512:
                    content = content[:509] + "..."
                v = f"> {content}"

                if len(item.attachments) >= 1:
                    v += f"\nplus {len(item.attachments)} attachment(s)"
                if len(item.embeds) >= 1:
                    v += f"\nplus {len(item.embeds)} embed(s)"

                emb.add_field(
                    name=f"{item.id} - {item.author.name}", value=v, inline=False
                )
            n = utils.Pagination.compute_total_pages(len(messages), L)
            emb.set_footer(
                text=f"Page {page}/{n} • For more information on a message, run /message-info."
            )
            return emb, n

        await utils.Pagination(interaction, get_page).navegate()

    else:
        await interaction.response.send_message(
            content=f"There are no messages between the bot and {user.mention}.",
            ephemeral=False,
        )


@bot.tree.command(
    name="message-info",
    description="Mod: Gets more info on a specific direct message to/from the bot.",
)
@appcmds.describe(user="The user.", message_id="The message ID.")
async def message_info(
    interaction: discord.Interaction, user: discord.User, message_id: str
):
    msg = await user.fetch_message(message_id)
    if msg:
        c = f"> {msg.content.replace("\n", "\n> ")}\n\\- {user.mention}\n"
        if len(msg.attachments) >= 1:
            c += "## Attachments"
            for att in msg.attachments:
                c += f"\n{att.url}"
        await interaction.response.send_message(content=c, embeds=msg.embeds)
    else:
        await interaction.response.send_message(
            content="There is no message with that user that has that ID."
        )


@bot.tree.command(
    name="view-message-file", description="MOD ONLY: View a message file."
)
@appcmds.choices(
    file=[
        appcmds.Choice(name="Rules", value="rules.txt"),
        appcmds.Choice(name="Receive Member Role", value="receive_member_role.txt"),
        appcmds.Choice(name="Ticket Message", value="ticket_message.txt"),
    ]
)
@appcmds.describe(
    file="The file to view.", raw="If you want the raw contents, set this to True."
)
async def view_message_file(interaction: discord.Interaction, file: str, raw: bool):
    mod_role = bot.get_guild(config.server_id).get_role(config.mod_role_id)
    if interaction.guild.id == config.server_id:
        if mod_role in interaction.user.roles:
            cont = open(f"./src/data/{file}", "r").read()

            if raw:
                await interaction.response.send_message(
                    content=f"{cont}", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    content=f"{utils.format_interaction_msg(cont, interaction)}",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                content="You don't have the required permissions to do this.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            content="This command can only be used in the BBC Fans server.",
            ephemeral=True,
        )


@bot.tree.context_menu(name="Update message file")
async def update_message_file(
    interaction: discord.Interaction, message: discord.Message
):
    files = [
        discord.SelectOption(label="Rules", value="rules.txt"),
        discord.SelectOption(
            label="Receive Member Role", value="receive_member_role.txt"
        ),
        discord.SelectOption(label="Ticket Message", value="ticket_message.txt"),
    ]

    class View(discord.ui.View):
        @discord.ui.select(cls=discord.ui.Select, options=files)
        async def select(
            self, interaction: discord.Interaction, select: discord.ui.Select
        ):
            mod_role = bot.get_guild(config.server_id).get_role(config.mod_role_id)
            if interaction.guild.id == config.server_id:
                if mod_role in interaction.user.roles:
                    f = open(f"./src/data/{select.values[0]}", "w")
                    f.write(message.content)

                    await interaction.response.send_message(
                        content=f"Updated {select.values[0]}", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        content="You don't have the required permissions to do this.",
                        ephemeral=True,
                    )
            else:
                await interaction.response.send_message(
                    content="This command can only be used in the BBC Fans server.",
                    ephemeral=True,
                )

            await interaction.message.edit(
                content=f"{select.values[0]} updated", view=None
            )

    await interaction.response.send_message(
        content="Choose a file to update", view=View()
    )


@bot.command()
async def bbcd(ctx: commands.Context) -> None:
    async with ctx.typing():
        release_info = requests.get(
            "https://api.github.com/repos/playsamay4/BBCD3_Desktop/releases"
        ).json()[0]

        embed = discord.Embed()
        embed.title = release_info["name"]
        embed.description = release_info["body"]
        embed.colour = discord.Colour(0x3FB93C)
        embed.url = release_info["html_url"]
        embed.set_author(
            name=release_info["author"]["login"],
            icon_url=release_info["author"]["avatar_url"],
            url=release_info["author"]["url"],
        )
        embed.timestamp = datetime.fromisoformat(
            release_info["published_at"].replace("Z", "+00:00")
        )

        await ctx.send(embed=embed)


bot.run(config.discord_token)
