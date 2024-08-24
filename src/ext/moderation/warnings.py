import discord
import discord.ext.commands as commands
import config
from models.moderation import ModerationWarning
from datetime import datetime
import peewee


@discord.app_commands.command(name="warn", description="(MODS ONLY) Warns a user.")
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to warn.",
    content="The reason for the warning.",
    proof="Any proof you'd like to add on to the warning. Ex: Message links",
    rule="If a rule was violated, what rule was it?",
    dm="Whether or not to DM the user about this warning. Defaults to True.",
)
async def add_warning(
    interaction: discord.Interaction,
    user: discord.Member,
    content: str,
    proof: str = None,
    rule: int = None,
    dm: bool = True,
):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        created = ModerationWarning.create(
            user_id=user.id,
            content=content,
            proof=proof,
            created_by=interaction.user.id,
            created_at=int(datetime.now().timestamp()),
            rule=rule,
        )

        conf_embed = discord.Embed(
            title=f"{user.name} has been warned.",
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

        if dm:
            try:
                await user.send(embed=dm_embed)
            except:
                pass

        await interaction.response.send_message(embed=conf_embed)
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@discord.app_commands.command(
    name="warnings", description="(MODS ONLY) Views all warnings on a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to get warnings for.", rule="Filter by violations of this rule."
)
async def warnings(
    interaction: discord.Interaction, user: discord.Member, rule: int = None
):
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
                ModerationWarning.select()
                .where(ModerationWarning.user_id == user.id)
                .where(ModerationWarning.rule == rule)[:25]
            )

            e = discord.Embed(title=f"Warnings for {user.name}")

            if len(q) == 0:
                await interaction.response.send_message(
                    content=f"*{user.name} has no warnings tagged with rule {rule}.*",
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
            q = ModerationWarning.select().where(ModerationWarning.user_id == user.id)[
                :25
            ]

            e = discord.Embed(title=f"Warnings for {user.name}")

            if len(q) == 0:
                await interaction.response.send_message(
                    content=f"*{user.name} has no warnings.*", ephemeral=True
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
    name="warning-info", description="(MODS ONLY) Views info on a specific warning."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(warning_id="The ID of the warning to get info on.")
async def warning_info(interaction: discord.Interaction, warning_id: int):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        try:
            q = ModerationWarning.get_by_id(warning_id)

            e = discord.Embed(title=f"Warning {warning_id}")

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
                content="That warning ID doesn't exist.", ephemeral=True
            )
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@discord.app_commands.command(
    name="remove-warning", description="(MODS ONLY) Removes a warning from a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(warning_id="The ID of the warning to remove.")
async def remove_warning(interaction: discord.Interaction, warning_id: int):
    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        try:
            a = ModerationWarning.get_by_id(warning_id)

            a.delete_instance()

            await interaction.response.send_message(
                content=f"Warning {warning_id} has been deleted.", ephemeral=True
            )
        except peewee.DoesNotExist:
            await interaction.response.send_message(
                content=f"A warning with the ID {warning_id} doesn't exist.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


def add_commands(bot: commands.Bot):
    bot.tree.add_command(add_warning)
    bot.tree.add_command(warnings)
    bot.tree.add_command(warning_info)
    bot.tree.add_command(remove_warning)
