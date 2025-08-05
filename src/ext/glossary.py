import discord
from discord.ext import commands
from discord import app_commands as appcmds
import database
import config
from datetime import datetime
from datetime import timezone
import utils
from logging import getLogger

log = getLogger("discord.fansbot.ext.glossary")


@appcmds.command(
    name="glossary", description="Common acronym/term/emoji in the server."
)
@appcmds.guild_only()
@appcmds.describe(query="Serach for a acronym/term/emoji.")
async def glossary(interaction: discord.Interaction, query: str = None):
    await interaction.response.defer()

    # get data
    d = database.GlossaryTerm.select()

    if query:
        d = d.where(database.GlossaryTerm.title.ilike(f"{query}%"))

    if len(d) == 0:
        await interaction.followup.send(content="No terms were found.")
        return

    L = 9  # elements per page

    async def get_page(page: int):
        emb = discord.Embed(title="BBC Fans Glossary", color=discord.Color.blue())
        offset = (page - 1) * L
        for item in d[offset : offset + L]:
            emb.add_field(name=item.title, value=item.description)
        emb.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        n = utils.Pagination.compute_total_pages(len(d), L)
        emb.set_footer(text=f"Page {page}/{n}")
        return emb, n

    await utils.Pagination(interaction, get_page).navegate()


@appcmds.command(
    name="add-glossary-term",
    description="Mod/Helper: Add a common acronym/term/emoji to the glossary.",
)
@appcmds.guild_only()
@appcmds.describe(
    title="The acronym/term/emoji of the entry.",
    description="The meaning of the acronym/term/emoji.",
    _type="The type of term.",
)
@appcmds.choices(
    _type=[
        appcmds.Choice(name="Acronym", value="ACRONYM"),
        appcmds.Choice(name="Term", value="TERM"),
        appcmds.Choice(name="Emoji", value="EMOJI"),
        appcmds.Choice(name="Other", value="OTHER"),
    ]
)
@appcmds.rename(_type="type")
async def add_glossary(
    interaction: discord.Interaction,
    title: str,
    description: str,
    _type: str,
):
    if config.MOD_ROLE_ID in [
        role.id for role in interaction.user.roles
    ] or config.HELPER_ROLE_ID in [role.id for role in interaction.user.roles]:
        await interaction.response.defer()

        _type = database.GlossaryTermType[_type]

        d = database.GlossaryTerm.create(
            created_by=str(interaction.user.id),
            title=title,
            description=description,
            term_type=_type,
            editors=[str(interaction.user.id)],
        )

        reply_embed = discord.Embed(
            title="Added glossary term",
            description=f"> **Title:** {d.title}\n> **Description:** {d.description}\n> **ID:** {d.id}\n> **Type:** {d.term_type.value}",
            color=discord.Color.blue(),
        )
        reply_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )
        reply_embed.timestamp = datetime.now()

        await interaction.followup.send(embed=reply_embed)
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@appcmds.command(
    name="edit-glossary-term",
    description="Mod/Helper: Change an entry in the glossary.",
)
@appcmds.guild_only()
@appcmds.describe(id="The ID of the entry.")
@utils.is_staff()
async def edit_glossary(
    interaction: discord.Interaction,
    id: int,
):
    if config.MOD_ROLE_ID in [
        role.id for role in interaction.user.roles
    ] or config.HELPER_ROLE_ID in [role.id for role in interaction.user.roles]:
        d = database.GlossaryTerm.select().where(database.GlossaryTerm.id == id)

        if len(d) == 0:
            await interaction.response.send_message(
                content=f"No terms with ID `{id}` were found."
            )
            return
        else:

            class EditTermModal(discord.ui.Modal, title=f"Edit Term #{id}"):
                new_title = discord.ui.TextInput(
                    label="Title",
                    required=True,
                    placeholder="The acronym, emoji, phrase, etc.",
                    style=discord.TextStyle.short,
                    default=d[0].title,
                )
                new_description = discord.ui.TextInput(
                    label="Description",
                    required=True,
                    placeholder="The meaning of the acronym, emoji, phrase, etc.",
                    style=discord.TextStyle.paragraph,
                    default=d[0].description,
                )
                new_type = discord.ui.TextInput(
                    label="Type",
                    required=True,
                    placeholder="The type of the entry.",
                    style=discord.TextStyle.short,
                    default=d[0].term_type.value,
                )

                async def on_submit(self, interaction: discord.Interaction):
                    await interaction.response.defer()

                    old_title = d[0].title
                    old_description = d[0].description
                    old_type = d[0].term_type

                    if self.new_type.value.upper() not in ["ACRONYM", "TERM", "EMOJI"]:
                        d[0].term_type = database.GlossaryTermType.OTHER
                    else:
                        d[0].term_type = database.GlossaryTermType[
                            self.new_type.value.upper()
                        ]

                    d[0].title = self.new_title.value
                    d[0].description = self.new_description.value
                    d[0].last_updated = datetime.now(timezone.utc).isoformat()

                    if str(interaction.user.id) not in d[0].editors:
                        d["editors"].append(str(interaction.user.id))

                    d[0].save()

                    resp_embed = discord.Embed(
                        title=f"Updated term #{id}", color=discord.Color.green()
                    )
                    if old_title is not d[0].title:
                        resp_embed.add_field(
                            name="Title",
                            value=f"{d[0].title}",
                            inline=False,
                        )
                    if old_description is not d[0].description:
                        resp_embed.add_field(
                            name="Description",
                            value=f"{d[0].description}",
                            inline=False,
                        )
                    if old_type is not d[0].term_type.value:
                        resp_embed.add_field(
                            name="Type",
                            value=f"{d[0].term_type.value}",
                            inline=False,
                        )
                    resp_embed.set_author(
                        name=interaction.user.name,
                        icon_url=interaction.user.display_avatar.url,
                    )
                    resp_embed.timestamp = datetime.now()

                    await interaction.followup.send(embed=resp_embed)

            await interaction.response.send_modal(EditTermModal())
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


@appcmds.command(
    name="remove-glossary-term",
    description="Mod/Helper: Remove an entry in the glossary.",
)
@appcmds.guild_only()
@appcmds.describe(id="The ID of the entry.")
@utils.is_staff()
async def remove_glossary(
    interaction: discord.Interaction,
    id: int,
):
    if config.MOD_ROLE_ID in [
        role.id for role in interaction.user.roles
    ] or config.HELPER_ROLE_ID in [role.id for role in interaction.user.roles]:
        await interaction.response.defer()

        d = database.GlossaryTerm.select().where(database.GlossaryTerm.id == id)

        if len(d) == 0:
            await interaction.followup.send(
                content=f"There is no term with the ID {id}."
            )
            return
        else:
            d[0].delete_instance()

            await interaction.followup.send(content=f"Deleted term #{id}")
    else:
        await interaction.response.send_message(
            content="You aren't allowed to run this command.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    bot.tree.add_command(glossary)
    bot.tree.add_command(add_glossary)
    bot.tree.add_command(edit_glossary)
    bot.tree.add_command(remove_glossary)

    log.info("Added glossary commands")
