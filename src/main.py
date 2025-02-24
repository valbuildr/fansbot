import time
import discord
import os
import config
from discord.ext import commands
from discord.ext import tasks
from random import choice
from models.moderation import (
    ModerationNote,
    ModerationWarning,
    ModerationMute,
    ModerationKick,
    ModerationBan,
)
import database
from ext.moderation import bans, kicks, mutes, notes, warnings
import requests
from datetime import datetime
import git

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
    ]

    chosen = choice(statuses)

    await bot.change_presence(activity=chosen)


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
        ]
    )

    bans.add_commands(bot)
    kicks.add_commands(bot)
    mutes.add_commands(bot)
    notes.add_commands(bot)
    warnings.add_commands(bot)

    change_status.start()


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
@discord.app_commands.guild_only()
async def rules(interaction: discord.Interaction) -> None:
    f = open("./src/data/rules.txt", "r")
    rules = f.read()

    await interaction.response.send_message(content=rules, ephemeral=True)
    f.close()


@bot.tree.context_menu(name="Update rules file")
async def update_rules_file(interacton: discord.Interaction, message: discord.Message):
    mod_role = bot.get_guild(config.server_id).get_role(config.mod_role_id)
    if interacton.guild.id == config.server_id:
        if mod_role in interacton.user.roles:
            f = open("./src/data/rules.txt", "w")
            f.write(message.content)

            await interacton.response.send_message(
                content="Updated the rules file!", ephemeral=True
            )
            f.close()
        else:
            await interacton.response.send_message(
                content="You don't have the required permissions to do this.",
                ephemeral=True,
            )
    else:
        await interacton.response.send_message(
            content="This command can only be used in the BBC Fans server.",
            ephemeral=True,
        )


@bot.tree.context_menu(name="Update member role file")
async def update_member_role_file(
    interacton: discord.Interaction, message: discord.Message
):
    mod_role = bot.get_guild(config.server_id).get_role(config.mod_role_id)
    if interacton.guild.id == config.server_id:
        if mod_role in interacton.user.roles:
            f = open("./src/data/receive_member_role.txt", "w")
            f.write(message.content)

            await interacton.response.send_message(
                content="Updated the member role file!", ephemeral=True
            )
            f.close()
        else:
            await interacton.response.send_message(
                content="You don't have the required permissions to do this.",
                ephemeral=True,
            )
    else:
        await interacton.response.send_message(
            content="This command can only be used in the BBC Fans server.",
            ephemeral=True,
        )


@bot.command(name="version")
async def version(ctx: commands.Context) -> None:
    local_repo = git.Repo(search_parent_directories=True)
    last_local_sha = local_repo.head.object.hexsha
    remote_repo = git.cmd.Git().ls_remote(config.source_code_link, heads=True)
    last_remote_sha = remote_repo.split(" ")[0]

    cont = f"Last local commit: [`{last_local_sha[:7]}`](<{config.source_code_link}/commit/{last_local_sha}>)\nSource code: <{config.source_code_link}>"

    if last_local_sha[:7] != last_remote_sha[:7]:
        cont += f"\n-# The local code is outdated, the last commit on Github is likely newer than what the bot is currently running. The latest commit on Github is [`{last_remote_sha[:7]}`](<{config.source_code_link}/commit/{last_remote_sha.split(" ")[0]}>)."

    await ctx.send(content=cont)


@bot.command()
async def tada(ctx: commands.Context) -> None:
    async with ctx.typing():
        await ctx.send(file=discord.File("./src/static/tada.mov"))
        return


@bot.command()
async def birthday(ctx: commands.Context):
    async with ctx.typing():
        await ctx.send(file=discord.File("./src/static/birthday.mp4"))
        return


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
