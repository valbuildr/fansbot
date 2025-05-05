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
import git
import utils
from logging import getLogger

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
            if archive_tag not in post.applied_tags and post.archived == False and post.locked == False:
                active_post = True
        
        main_cat = guild.get_channel(config.MAIN_CATEGORY_ID)
        other_cat = guild.get_channel(config.OTHER_CATEGORY_ID)

        if active_post:
            await channel.move(beginning=True, offset=1, category=main_cat)
        else:
            await channel.move(end=True, category=other_cat)


@bot.event
async def on_ready() -> None:
    change_status.start()
    auto_move_specials.start()

    await bot.load_extension("ext.tickets")
    await bot.load_extension("ext.moderation")

    log.info(f"Logged in as {bot.user.name}")


@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == config.server_id:
        await member.add_roles(discord.Object(id=config.unverified_role_id))


@bot.event
async def on_message(message: discord.Message):
    if message.channel.id == config.polls_channel_id and message.poll != None:
        await message.create_thread(name=message.poll.question)

    # censor bot bot
    if (
        message.author.id == 1091826653367386254
        and message.content == ":pepeAngryPing:"
    ):
        await message.delete()

    # even more bot bot censorship
    censor_nax_change = True
    if censor_nax_change:
        if message.author.id == 1091826653367386254 and len(message.embeds) == 1:
            if message.content == "<@&1174860300638507121>":
                if message.embeds[0].title in [
                    "News at One Moved",
                    "News at Six Moved",
                    "News at Ten Moved",
                ]:
                    if (
                        message.embeds[0].description.startswith("NAO has moved to")
                        or message.embeds[0].description.startswith("NAS has moved to")
                        or message.embeds[0].description.startswith("NAT has moved to")
                    ):
                        await message.delete()
                elif message.embeds[0].title == "New Program Detected":
                    pass  # do nothing for now, this might be changed if i implement fans bot pinging a different role when bot bot detects a new programme

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
@discord.app_commands.guild_only()
async def rules(interaction: discord.Interaction) -> None:
    f = open("./src/data/rules.txt", "r")
    rules = f.read()

    await interaction.response.send_message(content=rules, ephemeral=True)
    f.close()


@bot.tree.command(
    name="view-message-file", description="MOD ONLY: View a message file."
)
@discord.app_commands.choices(
    file=[
        discord.app_commands.Choice(name="Rules", value="rules.txt"),
        discord.app_commands.Choice(
            name="Receive Member Role", value="receive_member_role.txt"
        ),
        discord.app_commands.Choice(name="Ticket Message", value="ticket_message.txt"),
    ]
)
@discord.app_commands.describe(
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


@bot.command(name="version")
async def version(ctx: commands.Context) -> None:
    local_repo = git.Repo(search_parent_directories=True)
    last_local_sha = local_repo.head.object.hexsha

    cont = f"Last local commit: [`{last_local_sha[:7]}`](<{config.source_code_link}/commit/{last_local_sha}>)\nSource code: <{config.source_code_link}>"

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
