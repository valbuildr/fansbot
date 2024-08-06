import discord
import discord.ext.commands as commands
import config
import database
from datetime import datetime
import peewee


@discord.app_commands.command(name="kick", description="(MODS ONLY) Kicks a user.")
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to kick.",
    content="The reason for the kick.",
    proof="Any proof you'd like to add on to the kick. Ex: Message links",
    rule="If a rule was violated, what rule was it?",
)
async def add_kick(
    interaction: discord.Interaction,
    user: discord.Member,
    content: str,
    proof: str = None,
    rule: int = None,
):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        database.ModerationKick.create(
            user_id=user.id,
            content=content,
            proof=proof,
            created_by=interaction.user.id,
            created_at=int(datetime.now().timestamp()),
            rule=rule,
        )

        conf_embed = discord.Embed(
            title=f"{user.name} has been kicked.",
            description=f"> **Content:** {content}",
        )

        dm_embed = discord.Embed(
            title=f"You've been kicked in BBC Fans.",
            description=f"> **Content:** {content}",
        )

        if proof:
            conf_embed.description = conf_embed.description + f"\n> **Proof:** {proof}"
        if rule:
            conf_embed.description = conf_embed.description + f"\n> **Rule:** {rule}"
            dm_embed.description = dm_embed.description + f"\n> **Rule:** {rule}"

        try:
            await user.send(embed=dm_embed)
        except:
            pass

        await user.kick(reason=content)

        await interaction.response.send_message(embed=conf_embed)
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@discord.app_commands.command(
    name="kicks", description="(MODS ONLY) Views all kicks on a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to get kicks for.", rule="Filter by violations of this rule."
)
async def kicks(
    interaction: discord.Interaction, user: discord.Member, rule: int = None
):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        # this currently only shows the first 25. but once i figure out pagination, it'll be all.
        if rule:
            q = (
                database.ModerationKick.select()
                .where(database.ModerationKick.user_id == user.id)
                .where(database.ModerationKick.rule == rule)[:25]
            )

            e = discord.Embed(title=f"Kicks for {user.name}")

            if len(q) == 0:
                await interaction.response.send_message(
                    content=f"*{user.name} has no kicks tagged with rule {rule}.*",
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
            q = database.ModerationKick.select().where(
                database.ModerationKick.user_id == user.id
            )[:25]

            e = discord.Embed(title=f"Kicks for {user.name}")

            if len(q) == 0:
                await interaction.response.send_message(
                    content=f"*{user.name} has no kicks.*", ephemeral=True
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
    name="kick-info", description="(MODS ONLY) Views info on a specific kick."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(kick_id="The ID of the kick to get info on.")
async def kick_info(interaction: discord.Interaction, kick_id: int):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        try:
            q = database.ModerationKick.get_by_id(kick_id)

            e = discord.Embed(title=f"Warning {kick_id}")

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
                content="That kick ID doesn't exist.", ephemeral=True
            )
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@discord.app_commands.command(
    name="remove-kick", description="(MODS ONLY) Removes a kick from a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(kick_id="The ID of the kick to remove.")
async def remove_kick(interaction: discord.Interaction, kick_id: int):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    if mod_role in interaction.user.roles:
        try:
            a = database.ModerationKick.get_by_id(kick_id)

            a.delete_instance()

            await interaction.response.send_message(
                content=f"Kick {kick_id} has been deleted.", ephemeral=True
            )
        except peewee.DoesNotExist:
            await interaction.response.send_message(
                content=f"A kick with the ID {kick_id} doesn't exist.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


def add_commands(bot: commands.Bot):
    bot.tree.add_command(add_kick)
    bot.tree.add_command(kicks)
    bot.tree.add_command(kick_info)
    bot.tree.add_command(remove_kick)
