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
import database
from ext.moderation import bans, kicks, mutes, notes, warnings
import version

bot = commands.Bot(command_prefix="~", intents=discord.Intents.all())


bot.remove_command("help")


if not os.path.exists("src/data"):
    os.makedirs("src/data")


@bot.event
async def on_ready():
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


@bot.command()
@commands.is_owner()
@commands.dm_only()
async def sync(ctx: commands.Context):
    r = await ctx.send(content="Syncing...")
    await bot.tree.sync()
    await r.edit(content="Synced!")


@bot.tree.command(name="rules", description="Gets the server rules!")
@discord.app_commands.guild_only()
async def rules(interaction: discord.Interaction):
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


@bot.command()
async def v(ctx: commands.Context):
    await ctx.send(
        content=f"*Version {version.version}*\n*Source code: {version.source_code_link}*"
    )


bot.run(config.discord_token)
