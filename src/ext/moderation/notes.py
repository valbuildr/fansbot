import discord
import discord.ext.commands as commands
import config
from models.moderation import ModerationNote
from datetime import datetime
import peewee


@discord.app_commands.command(
    name="add-note", description="(MODS ONLY) Add a note onto a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to add a note on to.",
    content="The content of the note.",
    proof="Any proof you'd like to add on to the note. Ex: Message links",
    rule="If a rule was violated, what rule was it?",
)
async def add_note(
    interaction: discord.Interaction,
    user: discord.Member,
    content: str,
    proof: str = None,
    rule: int = None,
):
    await interaction.response.defer()

    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        ModerationNote.create(
            user_id=user.id,
            content=content,
            proof=proof,
            created_by=interaction.user.id,
            created_at=int(datetime.now().timestamp()),
            rule=rule,
        )

        e = discord.Embed(
            title=f"Note added to {user.name}.", description=f"> **Content:** {content}"
        )

        if proof:
            e.description = e.description + f"\n> **Proof:** {proof}"
        if rule:
            e.description = e.description + f"\n> **Rule:** {rule}"

        await interaction.followup.send(embed=e)
    else:
        await interaction.followup.send(
            content="You aren't allowed to run this command.",
        )


@discord.app_commands.command(
    name="notes", description="(MODS ONLY) Views all notes on a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    user="The user to get notes for.", rule="Filter by violations of this rule."
)
async def notes(
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
                ModerationNote.select()
                .where(ModerationNote.user_id == user.id)
                .where(ModerationNote.rule == rule)[:25]
            )

            e = discord.Embed(title=f"Notes for {user.name}")

            if len(q) == 0:
                await interaction.followup.send(
                    content=f"*{user.name} has no notes tagged with rule {rule}.*",
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
            q = ModerationNote.select().where(ModerationNote.user_id == user.id)[:25]

            e = discord.Embed(title=f"Notes for {user.name}")

            if len(q) == 0:
                await interaction.followup.send(
                    content=f"*{user.name} has no notes.*",
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
        await interaction.followup.send(
            content="You aren't allowed to run this command.",
        )


@discord.app_commands.command(
    name="note-info", description="(MODS ONLY) Views info on a specific note."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(note_id="The ID of the note to get info on.")
async def note_info(interaction: discord.Interaction, note_id: int):
    await interaction.response.defer()

    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        try:
            q = ModerationNote.get_by_id(note_id)

            e = discord.Embed(title=f"Note {note_id}")

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

            await interaction.followup.send(
                embed=e,
            )
        except peewee.DoesNotExist:
            await interaction.followup.send(
                content="That note ID doesn't exist.",
            )
    else:
        await interaction.followup.send(
            content="You aren't allowed to run this command.",
        )


@discord.app_commands.command(
    name="remove-note", description="(MODS ONLY) Removes a note from a user."
)
@discord.app_commands.guild_only()
@discord.app_commands.describe(note_id="The ID of the note to remove.")
async def remove_note(interaction: discord.Interaction, note_id: int):
    await interaction.response.defer()

    mod_role = interaction.client.get_guild(config.server_id).get_role(
        config.mod_role_id
    )
    helper_role = interaction.client.get_guild(config.server_id).get_role(
        config.helper_role_id
    )
    if mod_role in interaction.user.roles or helper_role in interaction.user.roles:
        try:
            a = ModerationNote.get_by_id(note_id)

            a.delete_instance()

            await interaction.followup.send(
                content=f"Note {note_id} has been deleted.",
            )
        except peewee.DoesNotExist:
            await interaction.followup.send(
                content=f"A note with the ID {note_id} doesn't exist.",
            )
    else:
        await interaction.followup.send(
            content="You aren't allowed to run this command.",
        )


def add_commands(bot: commands.Bot):
    bot.tree.add_command(add_note)
    bot.tree.add_command(notes)
    bot.tree.add_command(note_info)
    bot.tree.add_command(remove_note)
