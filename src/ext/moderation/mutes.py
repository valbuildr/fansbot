import discord
import discord.ext.commands as commands
import config
from models.moderation import ModerationMute
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
    dm="Whether or not to DM the user about this mute. Defaults to True.",
)
async def add_mute(
    interaction: discord.Interaction,
    user: discord.Member,
    content: str,
    length: str,
    proof: str = None,
    rule: int = None,
    dm: bool = True,
):
    await interaction.response.defer()

    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        # handle the length argument
        args = length.lower()
        matches = re.findall(time_regex, args)
        time = 0

        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                await interaction.followup.send(
                    content=f"{k} is an invalid time-key! h/m/s/d are valid!",
                )
                return
            except ValueError:
                await interaction.followup.send(
                    content=f"{v} is not a number!",
                )
                return

        a = datetime.now(ZoneInfo("Europe/London"))
        b = a + timedelta(seconds=time)

        created = ModerationMute.create(
            user_id=user.id,
            content=content,
            proof=proof,
            created_by=interaction.user.id,
            created_at=int(datetime.now().timestamp()),
            rule=rule,
        )

        # embeds
        conf_embed = discord.Embed(
            title=f"{user.name} has been muted.",
            description=f"> **Content:** {content}\n> **ID:** {created.id}",
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
        if dm:
            try:
                await user.send(embed=dm_embed)
            except:
                pass

        # finish
        await interaction.followup.send(embed=conf_embed)
    else:
        await interaction.followup.send(
            content="You aren't allowed to run this command."
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
    await interaction.response.defer()

    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        # this currently only shows the first 25. but once i figure out pagination, it'll be all.
        if rule:
            q = (
                ModerationMute.select()
                .where(ModerationMute.user_id == user.id)
                .where(ModerationMute.rule == rule)[:25]
            )

            e = discord.Embed(title=f"Mutes for {user.name}")

            if len(q) == 0:
                await interaction.followup.send(
                    content=f"*{user.name} has no mutes tagged with rule {rule}.*",
                )
            else:
                for entry in q:
                    e.add_field(
                        name=f"{entry.id}. {interaction.client.get_user(entry.created_by).name} - <t:{entry.created_at}:R>",
                        value=f"> {entry.content}",
                        inline=False,
                    )

                await interaction.followup.send(embed=e)
        else:
            q = ModerationMute.select().where(ModerationMute.user_id == user.id)[:25]

            e = discord.Embed(title=f"Mutes for {user.name}")

            if len(q) == 0:
                await interaction.followup.send(content=f"*{user.name} has no mutes.*")
            else:
                for entry in q:
                    e.add_field(
                        name=f"{entry.id}. {interaction.client.get_user(entry.created_by).name} - <t:{entry.created_at}:R>",
                        value=f"> {entry.content}",
                        inline=False,
                    )

                await interaction.followup.send(embed=e)
    else:
        await interaction.followup.send(
            content="You aren't allowed to run this command."
        )


@discord.app_commands.command(
    name="mute-info", description="(MODS ONLY) Views info on a specific mute."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(mute_id="The ID of the mute to get info on.")
async def mute_info(interaction: discord.Interaction, mute_id: int):
    await interaction.response.defer()

    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        try:
            q = ModerationMute.get_by_id(mute_id)

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

            await interaction.followup.send(embed=e)
        except peewee.DoesNotExist:
            await interaction.followup.send(content="That mute ID doesn't exist.")
    else:
        await interaction.followup.send(
            content="You aren't allowed to run this command."
        )


@discord.app_commands.command(
    name="remove-mute", description="(MODS ONLY) Removes a mute from a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(mute_id="The ID of the mute to remove.")
async def remove_mute(interaction: discord.Interaction, mute_id: int):
    await interaction.response.defer()

    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        try:
            a = ModerationMute.get_by_id(mute_id)

            a.delete_instance()

            await interaction.followup.send(content=f"Mute {mute_id} has been deleted.")
        except peewee.DoesNotExist:
            await interaction.followup.send(
                content=f"A mute with the ID {mute_id} doesn't exist.",
            )
    else:
        await interaction.followup.send(
            content="You aren't allowed to run this command."
        )


def add_commands(bot: commands.Bot):
    bot.tree.add_command(add_mute)
    bot.tree.add_command(mutes)
    bot.tree.add_command(mute_info)
    bot.tree.add_command(remove_mute)
