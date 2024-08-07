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

bot = commands.Bot(command_prefix="*", intents=discord.Intents.all())


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
    await interaction.response.send_message(
        content="# Server rules \n\n*(Last updated: 13 March 2024)*\n\n## 1. Be respectful\nTreat everyone with respect, whether they are in the server or not. Bullying, being rude or any politically-motivated hate towards others is not tolerated\n## 2. Drama\nDon't start arguments, drama or bring any unwanted negativity to the server\n## 3. Use the correct channels\nHelp keep the server organised by using dedicated channels if one is available. <#1016691910158590032> may be used for any purpose\n## 4. Doxxing\nRespect people's privacy. No sharing personal information of other members unless they have specifically said it's fine to do so\n## 5. Hate speech\nNo racism, sexism, transphobia, homophobia or any other hate speech\n## 6. Spam\nDon't flood channels with repetitive messages, bot commands, emojis, stickers or media. This does not apply to <#1097533655682912416> \n## 7. Pings\nNo ghost pinging (pinging someone then quickly deleting your message) or mass pinging people/roles. Be mindful of reply pings, some people don't like them\n## 8. NSFW content\nNo rude, explicit or inappropriate content\n## 9. Maturity\nWhile it's okay to have a bit of fun, please avoid any immature/childish behaviour. This does not apply to <#1112739833912250428>\n\nAdditional notes:\n- Timeouts, kicks or bans can be given for any other reason not listed above at the mods' discretion\n- BBC Fans is not affiliated with the BBC in any way\n- Please follow Discord's [Terms of Service](<https://discord.com/terms>)",
        ephemeral=True,
    )


@bot.command()
async def version(ctx: commands.Context):
    await ctx.send(content=f"*Version {config.version}*")


bot.run(config.discord_token)
