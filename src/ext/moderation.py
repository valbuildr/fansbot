import discord
from discord.ext import commands
from discord import app_commands as appcmds
from database import supabase_client
import config
from datetime import datetime
from datetime import timedelta
import utils
from logging import getLogger
import re

log = getLogger("discord.fansbot.ext.moderation")


table_name = "moderation_case"


def format_type(type: str):
    match type:
        case "NOTE":
            return "📝 Note"
        case "WARN":
            return "⚠️ Warn"
        case "MUTE":
            return "🔇 Mute"
        case "KICK":
            return "🥾 Kick"
        case "BAN":
            return "🔨 Ban"
        case _:
            return "🤷 Unknown"


def format_status(status: str):
    match status:
        case "OPEN":
            return "🟢 Open"
        case "CLOSED":
            return "🔴 Closed"
        case _:
            return "🤷 Unknown"


def parse_time_string(time_string: str):
    pattern = r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?"
    match = re.match(pattern, time_string)

    if match:
        days = int(match.group(1)) if match.group(1) else 0
        hours = int(match.group(2)) if match.group(2) else 0
        minutes = int(match.group(3)) if match.group(3) else 0
        seconds = int(match.group(4)) if match.group(4) else 0

        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    else:
        return None


def check_rules_list(rules_string: str):
    return all(s.isdigit() for s in rules_string)


@appcmds.command(name="add-note", description="Helper/Mod: Add a note onto a user.")
@appcmds.guild_only()
@appcmds.describe(
    user="The user to add a note on to",
    message="The note",
    proof="Peices of proof that may be relevant. Seperate peices with two commas and a space. e.x. '{peice_1},, {peice_2},, ...'",
    rules="Rule(s) violated. Seperate rules with one comma and a space. e.x. '1, 2, ...'",
)
async def add_note(
    interaction: discord.Interaction,
    user: discord.Member,
    message: str,
    proof: str = None,
    rules: str = None,
):
    if (
        interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles
        or interaction.guild.get_role(config.HELPER_ROLE_ID) in interaction.user.roles
    ):
        # defer response because we're dealing with databases
        await interaction.response.defer()

        # create dict for supabase
        d = {
            "user_id": str(user.id),
            "type": "NOTE",
            "status": "OPEN",
            "message": message,
            "created_by": str(interaction.user.id),
            "created_at": utils.dt_to_timestamp(datetime.now(), ""),
            "editors": [str(interaction.user.id)],
            "last_edited": utils.dt_to_timestamp(datetime.now(), ""),
            "is_test_data": config.IS_TEST_ENV,
        }

        # add proof to supabase dict, if applicable
        if proof:
            d["proof"] = proof.split(",, ")
        # add rules to supabase dict, if applicable
        if rules:
            r = rules.split(", ")
            if check_rules_list(rules) == False:
                await interaction.followup.send(
                    content="Please provide numbers for the 'rules' parameter."
                )
                return
            d["rules"] = rules.split(", ")

        # send data over to supabase
        data = supabase_client.table(table_name).insert(d).execute()

        # create reply embed
        reply_embed = discord.Embed(
            title=f"Note added to {user.name}",
            colour=discord.Colour.green(),
            description=f"> **Message:** {message}\n",
        )
        reply_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if rules:
            reply_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            reply_embed.add_field(name="Proof", value=v)
        reply_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        reply_embed.timestamp = datetime.now()

        # create log embed
        log_embed = discord.Embed(
            title=f"Note added to {user.name}",
            colour=discord.Colour.blue(),
            description=f"> **Message:** {message}\n",
        )
        log_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if rules:
            log_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            log_embed.add_field(name="Proof", value=v)
        log_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        log_embed.timestamp = datetime.now()

        # get log channel and send log embed to it
        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
        await log_channel.send(embed=log_embed)

        # reply
        await interaction.followup.send(embed=reply_embed)


@appcmds.command(name="warn", description="Helper/Mod: Warn a user.")
@appcmds.guild_only()
@appcmds.describe(
    user="The user to warn",
    message="The warning's message",
    proof="Peices of proof that may be relevant. Seperate peices with two commas and a space. e.x. '{peice_1},, {peice_2},, ...'",
    rules="Rule(s) violated. Seperate rules with one comma and a space. e.x. '1, 2, ...'",
    dm="Whether or not to DM the user. Defaults to True",
)
async def warn(
    interaction: discord.Interaction,
    user: discord.Member,
    message: str,
    proof: str = None,
    rules: str = None,
    dm: bool = True,
):
    if (
        interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles
        or interaction.guild.get_role(config.HELPER_ROLE_ID) in interaction.user.roles
    ):
        # defer response because we're dealing with databases
        await interaction.response.defer()

        # create dict for supabase
        d = {
            "user_id": str(user.id),
            "type": "WARN",
            "status": "OPEN",
            "message": message,
            "created_by": str(interaction.user.id),
            "created_at": utils.dt_to_timestamp(datetime.now(), ""),
            "editors": [str(interaction.user.id)],
            "last_edited": utils.dt_to_timestamp(datetime.now(), ""),
            "is_test_data": config.IS_TEST_ENV,
        }

        # add proof to supabase dict, if applicable
        if proof:
            d["proof"] = proof.split(",, ")
        # add rules to supabase dict, if applicable
        if rules:
            r = rules.split(", ")
            if check_rules_list(rules) == False:
                await interaction.followup.send(
                    content="Please provide numbers for the 'rules' parameter."
                )
                return
            d["rules"] = rules.split(", ")

        # send data over to supabase
        data = supabase_client.table(table_name).insert(d).execute()

        if dm:
            # create dm embed
            dm_embed = discord.Embed(
                title="You've been warned in BBC Fans",
                colour=discord.Colour.yellow(),
                description=f"> **Message from moderator:** {message}\n",
            )
            dm_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
            if rules:
                dm_embed.description += f"> **Rule(s) violated:** {rules}\n"
            dm_embed.timestamp = datetime.now()

            # create dm view
            dm_view = discord.ui.View(timeout=None)
            dm_appeal_button = discord.ui.Button(
                label="Appeal",
                style=discord.ButtonStyle.secondary,
                custom_id="appeal_warnings",
            )
            dm_view.add_item(dm_appeal_button)

            # try to send dm embed to user
            could_dm_user = False
            try:
                await user.send(embed=dm_embed, view=dm_view)
                could_dm_user = True
            except:
                pass

        # create reply embed
        reply_embed = discord.Embed(
            title=f"{user.name} was warned",
            colour=discord.Colour.green(),
            description=f"> **Message:** {message}\n",
        )
        reply_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if dm:
            reply_embed.description += (
                f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
            )
        if rules:
            reply_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            reply_embed.add_field(name="Proof", value=v)
        reply_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        reply_embed.timestamp = datetime.now()

        # create log embed
        log_embed = discord.Embed(
            title=f"{user.name} was warned",
            colour=discord.Colour.blue(),
            description=f"> **Message:** {message}\n",
        )
        log_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if dm:
            log_embed.description += (
                f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
            )
        if rules:
            log_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            log_embed.add_field(name="Proof", value=v)
        log_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        log_embed.timestamp = datetime.now()

        # get log channel and send log embed to it
        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
        await log_channel.send(embed=log_embed)

        # reply
        await interaction.followup.send(embed=reply_embed)


async def mute_length_autocomplete(interaction: discord.Interaction, current: str):
    return [
        appcmds.Choice(name="1 minute", value="1m"),
        appcmds.Choice(name="5 minutes", value="5m"),
        appcmds.Choice(name="10 minutes", value="10m"),
        appcmds.Choice(name="15 minutes", value="15m"),
        appcmds.Choice(name="30 minutes", value="30m"),
        appcmds.Choice(name="1 hour", value="1h"),
        appcmds.Choice(name="3 hours", value="3h"),
        appcmds.Choice(name="6 hours", value="6h"),
        appcmds.Choice(name="12 hours", value="12h"),
        appcmds.Choice(name="1 day", value="1d"),
        appcmds.Choice(name="3 days", value="3d"),
        appcmds.Choice(name="7 days", value="7d"),
        appcmds.Choice(name="14 days", value="14d"),
        appcmds.Choice(name="28 days (max)", value="28d"),
    ]


@appcmds.command(name="mute", description="Helper/Mod: Mute a user.")
@appcmds.guild_only()
@appcmds.describe(
    user="The user to mute",
    message="The mute's message",
    length="The mute's length",
    proof="Peices of proof that may be relevant. Seperate peices with two commas and a space. e.x. '{peice_1},, {peice_2},, ...'",
    rules="Rule(s) violated. Seperate rules with one comma and a space. e.x. '1, 2, ...'",
    dm="Whether or not to DM the user. Defaults to True",
)
@appcmds.autocomplete(length=mute_length_autocomplete)
async def mute(
    interaction: discord.Interaction,
    user: discord.Member,
    message: str,
    length: str,
    proof: str = None,
    rules: str = None,
    dm: bool = True,
):
    if (
        interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles
        or interaction.guild.get_role(config.HELPER_ROLE_ID) in interaction.user.roles
    ):
        # defer response because we're dealing with databases
        await interaction.response.defer()

        len = parse_time_string(length.lower())

        # discord limits timeouts to 28 days
        if len.total_seconds() > 2419200:
            await interaction.followup.send(
                content="Discord limits timeouts to 28 days. Please input a different length thats under 28 days."
            )
            return
        else:
            # create dict for supabase
            d = {
                "user_id": str(user.id),
                "type": "MUTE",
                "status": "OPEN",
                "message": message,
                "created_by": str(interaction.user.id),
                "created_at": utils.dt_to_timestamp(datetime.now(), ""),
                "expires": str(utils.dt_to_timestamp(datetime.now() + len, "")),
                "editors": [str(interaction.user.id)],
                "last_edited": utils.dt_to_timestamp(datetime.now(), ""),
                "is_test_data": config.IS_TEST_ENV,
            }

            # add proof to supabase dict, if applicable
            if proof:
                d["proof"] = proof.split(",, ")
            # add rules to supabase dict, if applicable
            if rules:
                r = rules.split(", ")
                if check_rules_list(rules) == False:
                    await interaction.followup.send(
                        content="Please provide numbers for the 'rules' parameter."
                    )
                    return
                d["rules"] = rules.split(", ")

            # send data over to supabase
            data = supabase_client.table(table_name).insert(d).execute()

            if dm:
                # create dm embed
                dm_embed = discord.Embed(
                    title="You've been muted in BBC Fans",
                    colour=discord.Colour.orange(),
                    description=f"> **Message from moderator:** {message}\n",
                )
                dm_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
                dm_embed.description += f"> **Length:** {length.lower()} (expires {utils.dt_to_timestamp(datetime.now() + len, 'F')})\n"
                if rules:
                    dm_embed.description += f"> **Rule(s) violated:** {rules}\n"
                dm_embed.timestamp = datetime.now()

                # create dm view
                dm_view = discord.ui.View(timeout=None)
                dm_appeal_button = discord.ui.Button(
                    label="Appeal",
                    style=discord.ButtonStyle.secondary,
                    custom_id="appeal_mutes",
                )
                dm_view.add_item(dm_appeal_button)

                # try to send dm embed to user
                could_dm_user = False
                try:
                    await user.send(embed=dm_embed, view=dm_view)
                    could_dm_user = True
                except:
                    pass

            # create reply embed
            reply_embed = discord.Embed(
                title=f"{user.name} was muted",
                colour=discord.Colour.green(),
                description=f"> **Message:** {message}\n",
            )
            reply_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
            reply_embed.description += f"> **Length:** {length.lower()} (expires {utils.dt_to_timestamp(datetime.now() + len, 'F')})\n"
            if dm:
                reply_embed.description += (
                    f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
                )
            if rules:
                reply_embed.description += f"> **Rule(s):** {rules}\n"
            if proof:
                v = ""
                for p in proof.split(",, "):
                    v += f"- {p}\n"
                reply_embed.add_field(name="Proof", value=v)
            reply_embed.set_author(
                name=interaction.user.name, icon_url=interaction.user.display_avatar.url
            )
            reply_embed.timestamp = datetime.now()

            # create log embed
            log_embed = discord.Embed(
                title=f"{user.name} was muted",
                colour=discord.Colour.blue(),
                description=f"> **Message:** {message}\n",
            )
            log_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
            log_embed.description += f"> **Length:** {length.lower()} (expires {utils.dt_to_timestamp(datetime.now() + len, 'F')})\n"
            if dm:
                log_embed.description += (
                    f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
                )
            if rules:
                log_embed.description += f"> **Rule(s):** {rules}\n"
            if proof:
                v = ""
                for p in proof.split(",, "):
                    v += f"- {p}\n"
                log_embed.add_field(name="Proof", value=v)
            log_embed.set_author(
                name=interaction.user.name, icon_url=interaction.user.display_avatar.url
            )
            log_embed.timestamp = datetime.now()

            # get log channel and send log embed to it
            log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
            await log_channel.send(embed=log_embed)

            # mute user
            await user.timeout(len, reason=message)

            # reply
            await interaction.followup.send(embed=reply_embed)


@appcmds.command(name="kick", description="Mod: Kick a user.")
@appcmds.guild_only()
@appcmds.describe(
    user="The user to kick",
    message="The kick's message",
    proof="Peices of proof that may be relevant. Seperate peices with two commas and a space. e.x. '{peice_1},, {peice_2},, ...'",
    rules="Rule(s) violated. Seperate rules with one comma and a space. e.x. '1, 2, ...'",
    dm="Whether or not to DM the user. Defaults to True",
)
async def kick(
    interaction: discord.Interaction,
    user: discord.Member,
    message: str,
    proof: str = None,
    rules: str = None,
    dm: bool = True,
):
    if interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles:
        # defer response because we're dealing with databases
        await interaction.response.defer()

        # create dict for supabase
        d = {
            "user_id": str(user.id),
            "type": "KICK",
            "status": "OPEN",
            "message": message,
            "created_by": str(interaction.user.id),
            "created_at": utils.dt_to_timestamp(datetime.now(), ""),
            "editors": [str(interaction.user.id)],
            "last_edited": utils.dt_to_timestamp(datetime.now(), ""),
            "is_test_data": config.IS_TEST_ENV,
        }

        # add proof to supabase dict, if applicable
        if proof:
            d["proof"] = proof.split(",, ")
        # add rules to supabase dict, if applicable
        if rules:
            r = rules.split(", ")
            if check_rules_list(rules) == False:
                await interaction.followup.send(
                    content="Please provide numbers for the 'rules' parameter."
                )
                return
            d["rules"] = rules.split(", ")

        # send data over to supabase
        data = supabase_client.table(table_name).insert(d).execute()

        if dm:
            # create dm embed
            dm_embed = discord.Embed(
                title="You've been kicked from BBC Fans",
                colour=discord.Colour.red(),
                description=f"> **Message from moderator:** {message}\n",
            )
            dm_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
            if rules:
                dm_embed.description += f"> **Rule(s) violated:** {rules}\n"
            dm_embed.timestamp = datetime.now()

            # create dm view
            dm_view = discord.ui.View(timeout=None)
            dm_appeal_button = discord.ui.Button(
                label="Appeal",
                style=discord.ButtonStyle.secondary,
                custom_id="appeal_kicks",
            )
            dm_view.add_item(dm_appeal_button)

            # try to send dm embed to user
            could_dm_user = False
            try:
                await user.send(embed=dm_embed)
                could_dm_user = True
            except:
                pass

        # create reply embed
        reply_embed = discord.Embed(
            title=f"{user.name} was kicked",
            colour=discord.Colour.green(),
            description=f"> **Message:** {message}\n",
        )
        reply_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if dm:
            reply_embed.description += (
                f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
            )
        if rules:
            reply_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            reply_embed.add_field(name="Proof", value=v)
        reply_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        reply_embed.timestamp = datetime.now()

        # create log embed
        log_embed = discord.Embed(
            title=f"{user.name} was kicked",
            colour=discord.Colour.blue(),
            description=f"> **Message:** {message}\n",
        )
        log_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if dm:
            log_embed.description += (
                f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
            )
        if rules:
            log_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            log_embed.add_field(name="Proof", value=v)
        log_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        log_embed.timestamp = datetime.now()

        # get log channel and send log embed to it
        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
        await log_channel.send(embed=log_embed)

        # kick user
        await user.kick(reason=message)

        # reply
        await interaction.followup.send(embed=reply_embed)


@appcmds.command(name="ban", description="Mod: Permanently ban a user.")
@appcmds.guild_only()
@appcmds.describe(
    user="The user to ban",
    message="The ban's message",
    proof="Peices of proof that may be relevant. Seperate peices with two commas and a space. e.x. '{peice_1},, {peice_2},, ...'",
    rules="Rule(s) violated. Seperate rules with one comma and a space. e.x. '1, 2, ...'",
    dm="Whether or not to DM the user. Defaults to True",
)
async def ban(
    interaction: discord.Interaction,
    user: discord.Member,
    message: str,
    proof: str = None,
    rules: str = None,
    dm: bool = True,
):
    # TODO: Create system for ensuring multiple mods agree to a ban
    if interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles:
        # defer response because we're dealing with databases
        await interaction.response.defer()

        # create dict for supabase
        d = {
            "user_id": str(user.id),
            "type": "BAN",
            "status": "OPEN",
            "message": message,
            "created_by": str(interaction.user.id),
            "created_at": utils.dt_to_timestamp(datetime.now(), ""),
            "editors": [str(interaction.user.id)],
            "last_edited": utils.dt_to_timestamp(datetime.now(), ""),
            "is_test_data": config.IS_TEST_ENV,
        }

        # add proof to supabase dict, if applicable
        if proof:
            d["proof"] = proof.split(",, ")
        # add rules to supabase dict, if applicable
        if rules:
            r = rules.split(", ")
            if check_rules_list(rules) == False:
                await interaction.followup.send(
                    content="Please provide numbers for the 'rules' parameter."
                )
                return
            d["rules"] = rules.split(", ")

        # send data over to supabase
        data = supabase_client.table(table_name).insert(d).execute()

        if dm:
            # create dm embed
            dm_embed = discord.Embed(
                title="You've been banned from BBC Fans",
                colour=discord.Colour.red(),
                description=f"> **Message from moderator:** {message}\n",
            )
            dm_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
            if rules:
                dm_embed.description += f"> **Rule(s) violated:** {rules}\n"
            dm_embed.timestamp = datetime.now()

            # try to send dm embed to user
            could_dm_user = False
            try:
                await user.send(embed=dm_embed)
                could_dm_user = True
            except:
                pass

        # create reply embed
        reply_embed = discord.Embed(
            title=f"{user.name} was banned",
            colour=discord.Colour.green(),
            description=f"> **Message:** {message}\n",
        )
        reply_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if dm:
            reply_embed.description += (
                f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
            )
        if rules:
            reply_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            reply_embed.add_field(name="Proof", value=v)
        reply_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        reply_embed.timestamp = datetime.now()

        # create log embed
        log_embed = discord.Embed(
            title=f"{user.name} was banned",
            colour=discord.Colour.blue(),
            description=f"> **Message:** {message}\n",
        )
        log_embed.description += f"> **Case ID:** {data.data[0]['id']}\n"
        if dm:
            log_embed.description += (
                f"> **Could DM User:** {'Yes' if could_dm_user else 'No'}\n"
            )
        if rules:
            log_embed.description += f"> **Rule(s):** {rules}\n"
        if proof:
            v = ""
            for p in proof.split(",, "):
                v += f"- {p}\n"
            log_embed.add_field(name="Proof", value=v)
        log_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        log_embed.timestamp = datetime.now()

        # get log channel and send log embed to it
        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
        await log_channel.send(embed=log_embed)

        # ban user
        await user.ban(reason=message)

        # reply
        await interaction.followup.send(embed=reply_embed)


@appcmds.command(
    name="unban", description="Mod: Unbans a user. Does not close/remove the case."
)
@appcmds.guild_only()
@appcmds.describe(
    user_id="The ID of the user to unban",
)
async def unban(
    interaction: discord.Interaction,
    user_id: str,
):
    if interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles:
        # defer response
        await interaction.response.defer()

        # fetch user
        user = await interaction.client.fetch_user(user_id)

        # create reply embed
        reply_embed = discord.Embed(
            title=f"{user.name} was unbanned",
            colour=discord.Colour.green(),
        )
        reply_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        reply_embed.timestamp = datetime.now()

        # create log embed
        log_embed = discord.Embed(
            title=f"{user.name} was unbanned",
            colour=discord.Colour.blue(),
        )
        log_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        log_embed.timestamp = datetime.now()

        # get log channel and send log embed to it
        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
        await log_channel.send(embed=log_embed)

        # unban user
        await interaction.guild.unban(discord.Object(user_id))

        # reply
        await interaction.followup.send(embed=reply_embed)


class CaseManagement(appcmds.Group):
    @appcmds.command(
        name="search", description="Helper/Mod: Search through moderation cases."
    )
    @appcmds.guild_only()
    @appcmds.describe(
        user="Filter by user",
        type="Filter by type",
        created_by="Filter by who created the case",
        status="Filter by case status",
    )
    @appcmds.choices(
        type=[
            appcmds.Choice(name="Note", value="NOTE"),
            appcmds.Choice(name="Warn", value="WARN"),
            appcmds.Choice(name="Kick", value="KICK"),
            appcmds.Choice(name="Ban", value="BAN"),
        ],
        status=[
            appcmds.Choice(name="Open", value="OPEN"),
            appcmds.Choice(name="Closed", value="CLOSED"),
        ],
    )
    async def search(
        self,
        interaction: discord.Interaction,
        user: discord.User = None,
        type: str = None,
        created_by: discord.User = None,
        status: str = None,
    ):
        if (
            interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles
            or interaction.guild.get_role(config.HELPER_ROLE_ID)
            in interaction.user.roles
        ):
            # defer response because we're dealing with databases
            await interaction.response.defer()

            # get data
            data = supabase_client.table(table_name).select("*")
            if user:
                data = data.eq("user_id", str(user.id))
            if type:
                data = data.eq("type", type)
            if created_by:
                data = data.eq("created_by", str(created_by.id))
            if status:
                data = data.eq("status", status)
            data = data.execute()

            # ensure the bot sends a response even when there is no cases found
            if len(data.data) == 0:
                await interaction.followup.send(content="No cases found.")
                return

            L = 5  # elements per page

            # create pagination
            async def get_page(page: int):
                emb = discord.Embed(title="Case Search", colour=discord.Colour.blue())
                offset = (page - 1) * L
                for item in data.data[offset : offset + L]:
                    emb.add_field(
                        name=f"Case #{item['id']}",
                        value=f"> **Message:** {item['message']}\n> **User:** <@{item['user_id']}>\n> **Type:** {format_type(item['type'])}\n> **Created by:** <@{item['created_by']}>",
                        inline=False,
                    )
                emb.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )
                n = utils.Pagination.compute_total_pages(len(data.data), L)
                emb.set_footer(
                    text=f"Page {page}/{n} • For more info on a specific case, run /case info."
                )
                return emb, n

            await utils.Pagination(interaction, get_page).navegate()

    @appcmds.command(
        name="info", description="Helper/Mod: Get info on a specific moderation case."
    )
    @appcmds.guild_only()
    @appcmds.describe(
        id="The case ID to get info on",
    )
    async def info(
        self,
        interaction: discord.Interaction,
        id: int,
    ):
        if (
            interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles
            or interaction.guild.get_role(config.HELPER_ROLE_ID)
            in interaction.user.roles
        ):
            # defer response because we're dealing with databases
            await interaction.response.defer()

            # get data
            data = supabase_client.table(table_name).select("*").eq("id", id).execute()

            # check if any data is actually returned
            if len(data.data) <= 0:
                await interaction.followup.send(
                    content=f"No case with the ID {id} was found."
                )
                return
            else:
                reply_embed = discord.Embed(
                    title=f"Case #{id}", description="", color=discord.Color.blue()
                )
                reply_embed.description += f"> **User:** <@{data.data[0]['user_id']}> ({data.data[0]['user_id']})\n"
                reply_embed.description += (
                    f"> **Type:** {format_type(data.data[0]['type'])}\n"
                )
                reply_embed.description += f"> **Message:** {data.data[0]['message']}\n"
                reply_embed.description += f"> **Created by:** <@{data.data[0]['created_by']}> ({data.data[0]['created_by']})\n"
                reply_embed.description += (
                    f"> **Created at:** <t:{data.data[0]['created_at']}:F>\n"
                )
                reply_embed.description += (
                    f"> **Last edited:** <t:{data.data[0]['last_edited']}:F>\n"
                )
                reply_embed.description += (
                    f"> **Status:** {format_status(data.data[0]['status'])}\n"
                )
                if data.data[0]["proof"]:
                    v = ""

                    for p in data.data[0]["proof"]:
                        v += f"- {p}\n"

                    reply_embed.add_field(name="Proof Piece(s)", value=v, inline=False)
                if data.data[0]["rules"]:
                    reply_embed.description += f"> **Rule(s):** {str(data.data[0]['rules']).replace('[', '').replace(']', '')}\n"
                if data.data[0]["expires"]:
                    reply_embed.description += f"> **Expires:** <t:{data.data[0]['expires']}:F> (<t:{data.data[0]['expires']}:R>)\n"
                editors = ""
                for editor in data.data[0]["editors"]:
                    if editor == data.data[0]["created_by"]:
                        editors += f"- <@{editor}> (creator)\n"
                    else:
                        editors += f"- <@{editor}>\n"
                reply_embed.add_field(name="Editors", value=editors, inline=False)
                reply_embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )

                await interaction.followup.send(embed=reply_embed)

    @appcmds.command(name="close", description="Mod: Close a moderation case.")
    @appcmds.guild_only()
    @appcmds.describe(
        id="The ID of the case to close",
        dm="Whether or not to DM the user. Defaults to False. Not available for notes",
    )
    async def close(self, interaction: discord.Interaction, id: int, dm: bool = False):
        if interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles:
            # defer response because we're dealing with databases
            await interaction.response.defer()

            # get data
            data = supabase_client.table(table_name).select("*").eq("id", id).execute()

            # check if any data is actually returned
            if len(data.data) <= 0:
                await interaction.followup.send(
                    content=f"No case with the ID {id} was found."
                )
                return
            else:
                dm_sent = False

                if dm and data.data[0]["type"] != "NOTE":
                    dm_embed = discord.Embed(
                        title="One of your cases in BBC Fans has been closed.",
                        description=f"> **Message:** {data.data[0]['message']}\n> **Case ID:** {data.data[0]['id']}\n> **Created:** <t:{data.data[0]['created_at']}:F>",
                        color=discord.Color.blue(),
                    )
                    dm_embed.timestamp = datetime.now()

                    user = await interaction.client.fetch_user(data.data[0]["user_id"])

                    try:
                        await user.send(embed=dm_embed)
                        dm_sent = True
                    except:
                        pass

                # create reply embed
                reply_embed = discord.Embed(
                    title=f"Closed case #{id}",
                    color=discord.Color.green(),
                    description="",
                )
                reply_embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )
                if dm:
                    reply_embed.description += (
                        f"> **Could DM User:** {'Yes' if dm_sent else 'No'}"
                    )
                reply_embed.timestamp = datetime.now()

                # create log embed
                log_embed = discord.Embed(
                    title=f"Closed case #{id}",
                    color=discord.Color.blue(),
                    description="",
                )
                log_embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )
                if dm:
                    log_embed.description += (
                        f"> **Could DM User:** {'Yes' if dm_sent else 'No'}"
                    )
                log_embed.timestamp = datetime.now()

                # get log channel and send log embed to it
                log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
                await log_channel.send(embed=log_embed)

                # change data in supabase
                supabase_client.table(table_name).update({"status": "CLOSED"}).eq(
                    "id", id
                ).execute()

                # reply
                await interaction.followup.send(embed=reply_embed)

    @appcmds.command(
        name="remove", description="Mod: Completely remove a moderation case."
    )
    @appcmds.guild_only()
    @appcmds.describe(
        id="The ID of the case to close",
    )
    async def remove(self, interaction: discord.Interaction, id: int):
        if interaction.guild.get_role(config.MOD_ROLE_ID) in interaction.user.roles:
            # defer response because we're dealing with databases
            await interaction.response.defer()

            # get data
            data = supabase_client.table(table_name).select("*").eq("id", id).execute()

            # check if any data is actually returned
            if len(data.data) <= 0:
                await interaction.followup.send(
                    content=f"No case with the ID {id} was found."
                )
                return
            else:
                # create reply embed
                reply_embed = discord.Embed(
                    title=f"Removed case #{id}", color=discord.Color.green()
                )
                reply_embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )
                reply_embed.timestamp = datetime.now()

                # create log embed
                log_embed = discord.Embed(
                    title=f"Removed case #{id}",
                    color=discord.Color.blue(),
                    description="",
                )
                log_embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )
                log_embed.timestamp = datetime.now()

                # get log channel and send log embed to it
                log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL_ID)
                await log_channel.send(embed=log_embed)

                # change data in supabase
                supabase_client.table(table_name).delete().eq("id", id).execute()

                # reply
                await interaction.followup.send(embed=reply_embed)

    # TODO: Edit case


async def setup(bot: commands.Bot):
    bot.tree.add_command(add_note)
    bot.tree.add_command(warn)
    bot.tree.add_command(mute)
    bot.tree.add_command(kick)
    bot.tree.add_command(ban)
    bot.tree.add_command(unban)
    bot.tree.add_command(
        CaseManagement(name="case", description="Moderation case management")
    )

    log.info("Added moderation commands")
