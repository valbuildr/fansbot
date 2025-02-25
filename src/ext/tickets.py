import discord
from discord.ext import commands
import config
from datetime import datetime
import utils


class TicketCommands(discord.app_commands.Group):
    @discord.app_commands.command(name="create", description="Create a new ticket.")
    async def create(self, interaction: discord.Interaction):
        guild = interaction.client.get_guild(config.server_id)
        cat = guild.get_channel(config.ticket_category_id)
        mod_role = guild.get_role(config.mod_role_id)

        overwrites = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, attach_files=True, embed_links=True
        )

        ticket = await cat.create_text_channel(
            f'ticket-{utils.dt_to_timestamp(datetime.now(), "a")}',
            overwrites={
                interaction.user: overwrites,
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                mod_role: overwrites,
            },
        )

        msg_cont = utils.format_interaction_msg(
            open("./src/data/ticket_message.txt", "r").read(), interaction
        )

        await ticket.send(content=msg_cont)

        await interaction.response.send_message(
            content=f"Ticket created in {ticket.mention}.", ephemeral=True
        )

    @discord.app_commands.command(name="close", description="Close a ticket.")
    async def close(self, interaction: discord.Interaction):
        if (
            interaction.channel.category.id == config.ticket_category_id
            and interaction.channel.name.startswith("ticket-")
        ):
            overwrites = list(interaction.channel.overwrites.keys())

            new_overwrite = discord.PermissionOverwrite(
                read_messages=True, send_messages=False
            )

            for overwrite in overwrites:
                if overwrite.name != "@everyone" and overwrite.id != config.mod_role_id:
                    await interaction.channel.set_permissions(
                        overwrite, overwrite=new_overwrite
                    )

            await interaction.response.send_message(content="Ticket closed.")


async def setup(bot: commands.Bot):
    bot.tree.add_command(TicketCommands(name="ticket", description="ticket commands"))
