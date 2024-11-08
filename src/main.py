import discord
import os
import config
from discord.ext import commands
from models.moderation import (
    ModerationNote,
    ModerationWarning,
    ModerationMute,
    ModerationKick,
    ModerationBan,
)
from models.economy import Economy, WorkReplies
import database
from ext.moderation import bans, kicks, mutes, notes, warnings
import version
import json
import utils
from datetime import datetime
from zoneinfo import ZoneInfo

bot = commands.Bot(command_prefix="~", intents=discord.Intents.all())


if not os.path.exists("src/data"):
    os.makedirs("src/data")


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user.name}")
    database.db.create_tables(
        [
            ModerationNote,
            ModerationWarning,
            ModerationMute,
            ModerationKick,
            ModerationBan,
            Economy,
            WorkReplies,
        ]
    )

    bans.add_commands(bot)
    kicks.add_commands(bot)
    mutes.add_commands(bot)
    notes.add_commands(bot)
    warnings.add_commands(bot)

    await bot.load_extension("ext.economy")


@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == config.server_id:
        await member.add_roles(discord.Object(id=config.unverified_role_id))


@bot.event
async def on_message(message: discord.Message):
    if message.channel.id == config.polls_channel_id and message.poll != None:
        await message.create_thread(name=message.poll.question)

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


@bot.command(hidden=True)
@commands.guild_only()
async def rule_agreement_button(ctx: commands.Context) -> None:
    channel = bot.get_guild(config.server_id).get_channel(config.rules_channel_id)
    mod_role = bot.get_guild(config.server_id).get_role(config.mod_role_id)

    if mod_role in ctx.author.roles:
        v = discord.ui.View(timeout=None)
        b = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label="I agree!",
            custom_id="agree_to_rules",
        )
        v.add_item(b)

        await channel.send(view=v)


@bot.command()
@commands.is_owner()
@commands.dm_only()
async def sync(ctx: commands.Context) -> None:
    r = await ctx.send(content="Syncing...")
    await bot.tree.sync()
    await r.edit(content="Synced!")


@bot.tree.command(name="rules", description="Gets the server rules!")
@discord.app_commands.guild_only()
async def rules(interaction: discord.Interaction) -> None:
    msg = (
        await bot.get_guild(config.server_id)
        .get_channel(config.rules_channel_id)
        .fetch_message(config.rules_message_id)
    )

    msg = msg.content.split("\n")
    msg.pop()
    msg.pop()
    msg.pop()
    content = ""
    for line in msg:
        content = content + f"{line}\n"

    await interaction.response.send_message(
        content=content, ephemeral=True, suppress_embeds=True
    )


@bot.command(name="version")
async def v(ctx: commands.Context) -> None:
    await ctx.send(
        content=f"*Version {version.version}*\n*Source code: {version.source_code_link}*"
    )


@bot.command()
async def tada(ctx: commands.Context) -> None:
    async with ctx.typing():
        await ctx.send(file=discord.File("./src/static/tada.mov"))
        return


if not os.path.exists("src/data/counters.json"):
    with open("src/data/counters.json", "w") as file:
        file.write("{}")
        file.close()


@bot.group(name="counters", hidden=True)
@commands.has_role(config.mod_role_id)
async def counters(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        data = json.load(open("src/data/counters.json", "r"))

        e = discord.Embed(title="Days since...", color=0x367DB3)

        for entry in data.keys():
            time = utils.epoch_to_datetime(str(data[entry]["last"]))
            now = datetime.now()

            diff = now - time

            st = str(diff.days)

            st = (
                st.replace("0", ":zero:")
                .replace("1", ":one:")
                .replace("2", ":two:")
                .replace("3", ":three:")
                .replace("4", ":four:")
                .replace("5", ":five:")
                .replace("6", ":six:")
                .replace("7", ":seven:")
                .replace("8", ":eight:")
                .replace("9", ":nine:")
            )

            if len(e.fields) <= 25:
                if (
                    data[entry]["highest"] is None
                    or str(diff.days) > data[entry]["highest"]
                ):
                    data[entry]["highest"] = str(diff.days)

                st += f"\n-# Highest: {data[entry]["highest"]}"

                st = (
                    st.replace("0", ":zero:")
                    .replace("1", ":one:")
                    .replace("2", ":two:")
                    .replace("3", ":three:")
                    .replace("4", ":four:")
                    .replace("5", ":five:")
                    .replace("6", ":six:")
                    .replace("7", ":seven:")
                    .replace("8", ":eight:")
                    .replace("9", ":nine:")
                )

                e.add_field(name=data[entry]["name"], value=st)

        if len(e.fields) == 0:
            await ctx.send(content="No counters configured.")
        else:
            e.set_footer(
                text='Original data provided by mint corp™️. By "Highest", we either mean the highest since records began, or the highest we could be bothered to find out. mint corp™️ and/or val industries™️ accepts no liability for incorrect values.'
            )
            e.timestamp = datetime.now()
            json.dump(data, open("src/data/counters.json", "w"))
            await ctx.send(embed=e)


@counters.command(name="create", hidden=True)
@commands.has_role(config.mod_role_id)
async def create_counter(ctx: commands.Context, *name: str):
    name = " ".join(name)
    data = json.load(open("src/data/counters.json", "r"))

    last_entry = 0

    for entry in data.keys():
        last_entry += last_entry
        if data[entry]["name"] == name:
            return await ctx.reply(
                content=f"A counter with this name already exists as counter #{entry}.\n-# Use `reset-counter {entry}` to reset it, or `delete-counter {entry}` to delete it."
            )

    data[str(last_entry + 1)] = {
        "name": name,
        "last": utils.dt_to_timestamp(datetime.now(ZoneInfo("Europe/London"))),
    }

    json.dump(data, open("src/data/counters.json", "w"))

    return await ctx.send(content=f'Saved "{name}" as counter #{str(last_entry + 1)}.')


@counters.command(name="delete", hidden=True)
@commands.has_role(config.mod_role_id)
async def delete_counter(ctx: commands.Context, counter: int):
    data = json.load(open("src/data/counters.json", "r"))

    if str(counter) in data.keys():

        class Confirmation(discord.ui.View):
            @discord.ui.button(label="Yes, delete it.", style=discord.ButtonStyle.red)
            async def yes(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                del data[str(counter)]

                json.dump(data, open("src/data/counters.json", "w"))

                await interaction.message.edit(view=None)

                await interaction.response.send_message(
                    content=f"Counter #{counter} has been deleted."
                )

            @discord.ui.button(
                label="No, don't delete it.", style=discord.ButtonStyle.gray
            )
            async def no(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                await interaction.message.edit(view=None)

                await interaction.response.send_message(
                    content=f"Counter #{counter} has **not** been deleted."
                )

        await ctx.send(
            content=f'Are you sure you want to delete counter #{counter} ("{data[str(counter)]["name"]}")?',
            view=Confirmation(),
        )
    else:
        return await ctx.send(content=f"Counter #{counter} does not exist.")


@counters.command(name="reset", hidden=True)
@commands.has_role(config.mod_role_id)
async def reset_counter(ctx: commands.Context, counter: int):
    data = json.load(open("src/data/counters.json", "r"))

    if str(counter) in data.keys():

        class Confirmation(discord.ui.View):
            @discord.ui.button(label="Yes, reset it.", style=discord.ButtonStyle.red)
            async def yes(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                data[str(counter)]["last"] = utils.dt_to_timestamp(datetime.now(), "a")
                json.dump(data, open("src/data/counters.json", "w"))

                await interaction.message.edit(view=None)

                await interaction.response.send_message(
                    content=f"Counter #{counter} has been reset."
                )

            @discord.ui.button(
                label="No, don't reset it.", style=discord.ButtonStyle.gray
            )
            async def no(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                await interaction.message.edit(view=None)

                await interaction.response.send_message(
                    content=f"Counter #{counter} has **not** been reset."
                )

        await ctx.send(
            content=f'Are you sure you want to delete counter #{counter} ("{data[str(counter)]["name"]}")?',
            view=Confirmation(),
        )
    else:
        return await ctx.send(content=f"Counter #{counter} does not exist.")


@counters.command(name="data", hidden=True)
@commands.has_role(config.mod_role_id)
async def counter_data(ctx: commands.Context):
    f = open("src/data/counters.json", "r")

    await ctx.send(content=f"```json\n{f.read()}\n```")


@counters.command(name="list", hidden=True)
@commands.has_role(config.mod_role_id)
async def counter_list(ctx: commands.Context):
    data = json.load(open("src/data/counters.json", "r"))

    e = discord.Embed(title="Counter list")

    for entry in data.keys():
        if len(e.fields) <= 25:
            e.add_field(name=f"{entry}", value=f"{data[entry]["name"]}")

    if len(e.fields) == 0:
        await ctx.send(content="No counters configured.")
    else:
        e.timestamp = datetime.now()
        await ctx.send(embed=e)


@counters.command(name="set", hidden=True)
@commands.has_role(config.mod_role_id)
async def counter_set(ctx: commands.Context, counter: int, value: int):
    data = json.load(open("src/data/counters.json", "r"))

    time = utils.epoch_to_datetime(str(value))
    now = datetime.now()

    diff = now - time

    st = str(diff.days)

    st = (
        st.replace("0", ":zero:")
        .replace("1", ":one:")
        .replace("2", ":two:")
        .replace("3", ":three:")
        .replace("4", ":four:")
        .replace("5", ":five:")
        .replace("6", ":six:")
        .replace("7", ":seven:")
        .replace("8", ":eight:")
        .replace("9", ":nine:")
    )

    if str(counter) in data.keys():

        class Confirmation(discord.ui.View):
            @discord.ui.button(label="Yes, change it.", style=discord.ButtonStyle.red)
            async def yes(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                data[str(counter)]["last"] = value
                json.dump(data, open("src/data/counters.json", "w"))

                await interaction.message.edit(view=None)

                await interaction.response.send_message(
                    content=f"Counter #{counter} has been changed to {st} ({value})."
                )

            @discord.ui.button(
                label="No, don't change it.", style=discord.ButtonStyle.gray
            )
            async def no(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                await interaction.message.edit(view=None)

                await interaction.response.send_message(
                    content=f"Counter #{counter} has **not** been changed."
                )

        await ctx.send(
            content=f'Are you sure you want to change counter #{counter} ("{data[str(counter)]["name"]}") to {st} ({value})?',
            view=Confirmation(),
        )
    else:
        return await ctx.send(content=f"Counter #{counter} does not exist.")


bot.run(config.discord_token)
