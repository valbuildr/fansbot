import discord
from discord.ext import commands
from discord import app_commands as appcmds
from database import supabase_client
import config
from datetime import datetime
from datetime import timezone
import utils
from logging import getLogger
from supabase import SupabaseException

log = getLogger("discord.fansbot.ext.glossary")


table_name = "glossary"


@appcmds.command(
    name="glossary", description="Common acronym/term/emoji in the server."
)
@appcmds.guild_only()
@appcmds.describe(query="Serach for a acronym/term/emoji.")
async def glossary(interaction: discord.Interaction, query: str = None):
    await interaction.response.defer()

    # get data
    data = (
        supabase_client.table(table_name)
        .select("*")
        .eq("is_test_data", config.IS_TEST_ENV)
    )
    if query:
        data = data.ilike("title", f"{query}%")

    try:
        data = data.execute()
    except SupabaseException as err:
        log.error(err)
        await interaction.followup.send(content="A database error occurred.")
        return

    if len(data.data) == 0:
        await interaction.followup.send(content="No terms were found.")
        return

    L = 9  # elements per page

    async def get_page(page: int):
        emb = discord.Embed(title="BBC Fans Glossary", color=discord.Color.blue())
        offset = (page - 1) * L
        for item in data.data[offset : offset + L]:
            emb.add_field(name=item.get("title"), value=item.get("description"))
        emb.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
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

        o = {
            "created_by": str(interaction.user.id),
            "editors": [str(interaction.user.id)],
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
        try:
            data = (
                supabase_client.table(table_name).select("*").eq("id", id).execute()
            )  # this could cause interactions to fail, but it hasn't yet in my testing - val
        except SupabaseException as err:
            log.error(err)
            await interaction.response.send_message(
                content="A database error occurred."
            )
            return

        if len(data.data) == 0:
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
                    default=data.data[0].get("title"),
                )
                new_description = discord.ui.TextInput(
                    label="Description",
                    required=True,
                    placeholder="The meaning of the acronym, emoji, phrase, etc.",
                    style=discord.TextStyle.paragraph,
                    default=data.data[0].get("description"),
                )
                new_type = discord.ui.TextInput(
                    label="Type",
                    required=True,
                    placeholder="The type of the entry.",
                    style=discord.TextStyle.short,
                    default=data.data[0].get("type"),
                )

                async def on_submit(self, interaction: discord.Interaction):
                    await interaction.response.defer()

                    old_title = data.data[0].get("title")
                    old_description = data.data[0].get("description")
                    old_type = data.data[0].get("type")

                    d = {
                        "title": self.new_title.value,
                        "description": self.new_description.value,
                        "type": self.new_type.value.upper(),
                        "editors": data.data[0].get("editors"),
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                    }

                    if d["type"] not in ["ACRONYM", "TERM", "EMOJI"]:
                        d["type"] = "OTHER"

                    if str(interaction.user.id) not in d["editors"]:
                        d["editors"].append(str(interaction.user.id))

                    try:
                        r = (
                            supabase_client.table(table_name)
                            .update(d)
                            .eq("id", id)
                            .execute()
                        )
                    except SupabaseException as err:
                        log.error(err)
                        await interaction.followup.send(
                            content="A database error occurred."
                        )
                        return

                    resp_embed = discord.Embed(
                        title=f"Updated term #{id}", color=discord.Color.green()
                    )
                    if old_title is not d["title"]:
                        resp_embed.add_field(
                            name="Title",
                            value=f"{d['title']}",
                            inline=False,
                        )
                    if old_description is not d["description"]:
                        resp_embed.add_field(
                            name="Description",
                            value=f"{d['description']}",
                            inline=False,
                        )
                    if old_type is not d["type"]:
                        resp_embed.add_field(
                            name="Type",
                            value=f"{d['type']}",
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

        try:
            data = supabase_client.table(table_name).select("*").eq("id", id).execute()
        except SupabaseException as err:
            log.error(err)
            await interaction.followup.send(content="A database error occurred.")
            return
        except:
            log.error("Unknown error!")
            await interaction.followup.send(content="An unkown error occurred.")
            return

        if len(data.data) is 0:
            await interaction.followup.send(
                content=f"There is no term with the ID {id}."
            )
            return
        else:
            term = data.data[0]

            try:
                r = supabase_client.table(table_name).delete().eq("id", id).execute()
            except SupabaseException as err:
                log.error(err)
                await interaction.followup.send(content="A database error occurred.")
                return
            except:
                log.error("Unknown error!")
                await interaction.followup.send(content="An unkown error occurred.")
                return

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
