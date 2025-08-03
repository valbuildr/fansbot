import discord
from discord.ext import commands
from discord import app_commands as appcmds
from database import supabase_client
import config
from datetime import datetime
import utils
from logging import getLogger

log = getLogger("discord.fansbot.ext.glossary")


table_name = "glossary"


@appcmds.command(
    name="glossary", description="Common acronym/term/emoji in the server."
)
@appcmds.guild_only()
@appcmds.describe(query="Serach for a acronym/term/emoji.")
async def glossary(interaction: discord.Interaction, query: str = None):
    await interaction.response.defer()

    data = (
        supabase_client.table(table_name)
        .select("*")
        .eq("is_test_data", config.IS_TEST_ENV)
        .ilike("title", f"{query}%")
    )

    try:
        data = data.execute()
    except:
        await interaction.followup.send(content="An error ocurred.")
        return

    if len(data.data) == 0:
        await interaction.followup.send(content="No entries found.")
        return

    L = 10  # elements per page

    # create pagination
    async def get_page(page: int):
        emb = discord.Embed(title="BBC Fans Glossary", colour=discord.Colour.blue())
        offset = (page - 1) * L
        for item in data.data[offset : offset * L]:
            emb.add_field(
                name=f"{item["title"]}",
                value=f"{item["description"]}\n-# {item["id"]}",
                inline=False,
            )
        emb.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar.url,
        )
        n = utils.Pagination.compute_total_pages(len(data.data), L)
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
    type="The type of term.",
)
@appcmds.choices(
    type=[
        appcmds.Choice(name="Acronym", value="ACRONYM"),
        appcmds.Choice(name="Term", value="TERM"),
        appcmds.Choice(name="Emoji", value="EMOJI"),
        appcmds.Choice(name="Other", value="OTHER"),
    ]
)
@appcmds.rename(_type="type")
@utils.is_staff()
async def add_glossary(
    interaction: discord.Interaction,
    title: str,
    description: str,
    _type: str,
):
    await interaction.response.defer()

    o = {
        "created_by": str(interaction.user.id),
        "title": title,
        "description": description,
        "type": _type,
        "is_test_data": config.IS_TEST_ENV,
    }

    try:
        data = supabase_client.table(table_name).insert(o).execute()
    except:
        await interaction.followup.send(content="An error occurred.")
        return

    reply_embed = discord.Embed(
        title="Added glossary term",
        description=f"> **Title:** {data.data[0]["title"]}\n> **Description:** {data.data[0]["description"]}\n> **ID:** {data.data[0]["id"]}\n> **Type:** {data.data[0]["type"]}",
        color=discord.Color.blue(),
    )
    reply_embed.set_author(
        name=interaction.user.name, icon_url=interaction.user.display_avatar.url
    )
    reply_embed.timestamp = datetime.now()

    await interaction.followup.send(embed=reply_embed)


@appcmds.command(
    name="edit-glossary-term",
    description="Mod/Helper: Change an entry in the glossary.",
)
@appcmds.guild_only()
@appcmds.describe(
    id="The ID of the entry.",
    title="The new acronym/term/emoji of the entry.",
    description="The new meaning of the acronym/term/emoji.",
    _type="The new type of term.",
)
@appcmds.rename(_type="type")
@utils.is_staff()
async def edit_glossary(
    interaction: discord.Interaction,
    id: str,
    title: str = None,
    description: str = None,
    type: str = None,
): ...


@appcmds.command(
    name="remove-glossary-term",
    description="Mod/Helper: Remove an entry in the glossary.",
)
@appcmds.guild_only()
@appcmds.describe(
    id="The ID of the entry.",
)
@utils.is_staff()
async def remove_glossary(
    interaction: discord.Interaction,
    id: str,
): ...


async def setup(bot: commands.Bot):
    bot.tree.add_command(glossary)
    bot.tree.add_command(add_glossary)
    bot.tree.add_command(edit_glossary)
    bot.tree.add_command(remove_glossary)

    log.info("Added glossary commands")
