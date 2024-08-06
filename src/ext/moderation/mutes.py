import discord
import discord.ext.commands as commands
import config
import database
from datetime import datetime, timedelta
import peewee
from zoneinfo import ZoneInfo
import re


time_regex = re.compile("(?:(\\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


@discord.app_commands.command(name="mute", description="(MODS ONLY) Mutes a user.")
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to mute.",
    content="The reason for the mute.",
    length="How long to mute the user. (Use 2d 10h 3m 2s format!)",
    proof="Any proof you'd like to add on to the mute. Ex: Message links",
    rule="If a rule was violated, what rule was it?",
)
async def add_mute(
    interaction: discord.Interaction,
    user: discord.Member,
    content: str,
    length: str,
    proof: str = None,
    rule: int = None,
):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        # handle the length argument
        args = length.lower()
        matches = re.findall(time_regex, args)
        time = 0

        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                await interaction.response.send_message(
                    content=f"{k} is an invalid time-key! h/m/s/d are valid!",
                    ephemeral=True,
                )
                return
            except ValueError:
                await interaction.response.send_message(
                    content=f"{v} is not a number!",
                    ephemeral=True,
                )
                return

        a = datetime.now(ZoneInfo("Europe/London"))
        b = a + timedelta(seconds=time)

        database.ModerationMute.create(
            user_id=user.id,
            content=content,
            proof=proof,
            created_by=interaction.user.id,
            created_at=int(datetime.now().timestamp()),
            rule=rule,
        )

        # embeds
        conf_embed = discord.Embed(
            title=f"{user.name} has been nuted.",
            description=f"> **Content:** {content}",
        )

        dm_embed = discord.Embed(
            title=f"You've been warned in BBC Fans.",
            description=f"> **Content:** {content}",
        )

        if proof:
            conf_embed.description = conf_embed.description + f"\n> **Proof:** {proof}"
        if rule:
            conf_embed.description = conf_embed.description + f"\n> **Rule:** {rule}"
            dm_embed.description = dm_embed.description + f"\n> **Rule:** {rule}"

        # mute the user
        await user.timeout(b)

        # dms
        try:
            await user.send(embed=dm_embed)
        except:
            pass

        # finish
        await interaction.response.send_message(embed=conf_embed)
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@discord.app_commands.command(
    name="mutes", description="(MODS ONLY) Views all mutes on a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to get mutes for.", rule="Filter by violations of this rule."
)
async def mutes(
    interaction: discord.Interaction, user: discord.Member, rule: int = None
):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        # this currently only shows the first 25. but once i figure out pagination, it'll be all.
        if rule:
            q = (
                database.ModerationMute.select()
                .where(database.ModerationMute.user_id == user.id)
                .where(database.ModerationMute.rule == rule)[:25]
            )

            e = discord.Embed(title=f"Mutes for {user.name}")

            if len(q) == 0:
                await interaction.response.send_message(
                    content=f"*{user.name} has no mutes tagged with rule {rule}.*",
                    ephemeral=True,
                )
            else:
                for entry in q:
                    e.add_field(
                        name=f"{entry.id}. {interaction.client.get_user(entry.created_by).name} - <t:{entry.created_at}:R>",
                        value=f"> {entry.content}",
                        inline=False,
                    )

                await interaction.response.send_message(embed=e)
        else:
            q = database.ModerationMute.select().where(
                database.ModerationMute.user_id == user.id
            )[:25]

            e = discord.Embed(title=f"Mutes for {user.name}")

            if len(q) == 0:
                await interaction.response.send_message(
                    content=f"*{user.name} has no mutes.*", ephemeral=True
                )
            else:
                for entry in q:
                    e.add_field(
                        name=f"{entry.id}. {interaction.client.get_user(entry.created_by).name} - <t:{entry.created_at}:R>",
                        value=f"> {entry.content}",
                        inline=False,
                    )

                await interaction.response.send_message(embed=e)
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@discord.app_commands.command(
    name="mute-info", description="(MODS ONLY) Views info on a specific mute."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(mute_id="The ID of the mute to get info on.")
async def mute_info(interaction: discord.Interaction, mute_id: int):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        try:
            q = database.ModerationMute.get_by_id(mute_id)

            e = discord.Embed(title=f"Mute {mute_id}")

            e.add_field(
                name="On",
                value=f"{interaction.client.get_user(q.user_id).mention}",
                inline=False,
            )
            e.add_field(name="Content", value=f"{q.content}", inline=False)
            e.add_field(name="Proof", value=f"{q.proof}", inline=False)
            e.add_field(
                name="Created By",
                value=f"{interaction.client.get_user(q.created_by).mention}",
                inline=False,
            )
            e.add_field(
                name="Created At",
                value=f"<t:{q.created_at}:F> (<t:{q.created_at}:R>)",
                inline=False,
            )
            e.add_field(
                name="Rule Violated",
                value=f"{q.rule}",
                inline=False,
            )

            await interaction.response.send_message(embed=e, ephemeral=True)
        except peewee.DoesNotExist:
            await interaction.response.send_message(
                content="That mute ID doesn't exist.", ephemeral=True
            )
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@discord.app_commands.command(
    name="remove-mute", description="(MODS ONLY) Removes a mute from a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(mute_id="The ID of the mute to remove.")
async def remove_mute(interaction: discord.Interaction, mute_id: int):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        try:
            a = database.ModerationMute.get_by_id(mute_id)

            a.delete_instance()

            await interaction.response.send_message(
                content=f"Mute {mute_id} has been deleted.", ephemeral=True
            )
        except peewee.DoesNotExist:
            await interaction.response.send_message(
                content=f"A mute with the ID {mute_id} doesn't exist.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


def add_commands(bot: commands.Bot):
    bot.tree.add_command(add_mute)
    bot.tree.add_command(mutes)
    bot.tree.add_command(mute_info)
    bot.tree.add_command(remove_mute)
