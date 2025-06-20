import discord
from discord.ext import commands
import config
from datetime import datetime
import utils
from logging import getLogger
from discord import app_commands as appcmds

log = getLogger("discord.fansbot.ext.tickets")


class TicketCommands(appcmds.Group):
    @appcmds.command(name="create", description="Create a new ticket.")
    @appcmds.guild_only()
    async def create(self, interaction: discord.Interaction):
        guild = interaction.client.get_guild(config.server_id)
        cat = guild.get_channel(config.ticket_category_id)
        mod_role = guild.get_role(config.mod_role_id)

        class ConfirmationModal(discord.ui.Modal):
            reason = discord.ui.TextInput(
                label="Reason",
                placeholder="Why are you opening this ticket?",
                required=True,
            )

            async def on_submit(self, interaction: discord.Interaction):
                ticket = await cat.create_text_channel(
                    f'ticket-{utils.dt_to_timestamp(datetime.now(), "a")}',
                    overwrites={
                        interaction.user: discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,
                            attach_files=True,
                            embed_links=True,
                        ),
                        guild.default_role: discord.PermissionOverwrite(
                            read_messages=False
                        ),
                        mod_role: discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,
                            attach_files=True,
                            embed_links=True,
                        ),
                        interaction.client.user: discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,
                            attach_files=True,
                            embed_links=True,
                            manage_channels=True,
                        ),
                    },
                )

                v = discord.ui.LayoutView()
                c = discord.ui.Container()
                c.add_item(
                    discord.ui.TextDisplay(
                        f"## {interaction.user.mention} opened a ticket!\n**Reason provided by user:** {self.reason}\n\n**Please be patient, a staff member will be with you soon!**"
                    )
                )
                v.add_item(c)

                await ticket.send(view=v)

                await interaction.response.send_message(
                    content=f"Ticket created in {ticket.mention}.", ephemeral=True
                )

        await interaction.response.send_modal(
            ConfirmationModal(title="Create a Ticket")
        )

    @appcmds.command(name="close", description="Close a ticket.")
    @appcmds.guild_only()
    async def close(self, interaction: discord.Interaction):
        if (
            interaction.channel.category.id == config.ticket_category_id
            and interaction.channel.name.startswith("ticket-")
        ):
            overwrites = list(interaction.channel.overwrites.keys())

            for overwrite in overwrites:
                if (
                    overwrite.name != "@everyone"
                    and overwrite.id != config.mod_role_id
                    and overwrite.id != interaction.client.user.id
                ):
                    await interaction.channel.set_permissions(
                        overwrite,
                        overwrite=discord.PermissionOverwrite(
                            read_messages=True, send_messages=False
                        ),
                    )

            await interaction.response.send_message(
                content=f"Ticket closed by {interaction.user.mention}."
            )

            ticketid = interaction.channel.name.split("-")[1]
            await interaction.channel.edit(name=f"closed-{ticketid}")

    @appcmds.command(name="add-user", description="Mod: Add a user to ticket.")
    @appcmds.describe(
        user="The user to add to the ticket.",
        ping="Ping the user or not. Defaults to True.",
    )
    @appcmds.guild_only()
    async def add_user(
        self, interaction: discord.Interaction, user: discord.Member, ping: bool = True
    ):
        if (
            interaction.channel.category.id == config.ticket_category_id
            and interaction.channel.name.startswith("ticket-")
        ):
            overwrites = list(interaction.channel.overwrites.keys())

            overwrites_formatted = []
            for overwrite in overwrites:
                overwrites_formatted.append(overwrite.id)

            if user.id in overwrites_formatted:
                await interaction.response.send_message(
                    content="That user is already a part of this ticket.",
                    ephemeral=True,
                )
            else:
                await interaction.channel.set_permissions(
                    user,
                    overwrite=discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        attach_files=True,
                        embed_links=True,
                    ),
                )
                if ping:
                    await interaction.response.send_message(
                        content=f"Added {user.mention} to the ticket."
                    )
                else:
                    await interaction.response.send_message(
                        content=f"Added {user.mention} to the ticket.",
                        allowed_mentions=discord.AllowedMentions.none(),
                    )

    @appcmds.command(name="add-role", description="Mod: Add a role to ticket.")
    @appcmds.describe(
        role="The role to add to the ticket.",
        ping="Ping the role or not. Defaults to False.",
    )
    @appcmds.guild_only()
    async def add_role(
        self, interaction: discord.Interaction, role: discord.Role, ping: bool = False
    ):
        if (
            interaction.channel.category.id == config.ticket_category_id
            and interaction.channel.name.startswith("ticket-")
        ):
            overwrites = list(interaction.channel.overwrites.keys())

            overwrites_formatted = []
            for overwrite in overwrites:
                overwrites_formatted.append(overwrite.id)

            if role.id in overwrites_formatted:
                await interaction.response.send_message(
                    content="That role is already a part of this ticket.",
                    ephemeral=True,
                )
            else:
                await interaction.channel.set_permissions(
                    role,
                    overwrite=discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        attach_files=True,
                        embed_links=True,
                    ),
                )
                if ping:
                    await interaction.response.send_message(
                        content=f"Added {role.mention} to the ticket."
                    )
                else:
                    await interaction.response.send_message(
                        content=f"Added {role.mention} to the ticket.",
                        allowed_mentions=discord.AllowedMentions.none(),
                    )

    @appcmds.command(
        name="remove-user", description="Mod: Remove a user from a ticket."
    )
    @appcmds.describe(user="The user to remove")
    @appcmds.guild_only()
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member):
        if (
            interaction.channel.category.id == config.ticket_category_id
            and interaction.channel.name.startswith("ticket-")
        ):
            if user.id == interaction.user.id:
                await interaction.response.send_message(
                    content="You can not remove yourself from this ticket.",
                    ephemeral=True,
                )
            elif user.id == interaction.client.user.id:
                await interaction.response.send_message(
                    content="You can not remove the bot from this ticket.",
                    ephemeral=True,
                )
            else:
                await interaction.channel.set_permissions(
                    user,
                    overwrite=discord.PermissionOverwrite(
                        read_messages=False,
                        send_messages=False,
                    ),
                )

                await interaction.response.send_message(
                    content=f"Removed {user.mention} from the ticket.",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

    @appcmds.command(
        name="remove-role", description="Mod: Remove a role from a ticket."
    )
    @appcmds.guild_only()
    @appcmds.describe(role="The role to remove")
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role):
        if (
            interaction.channel.category.id == config.ticket_category_id
            and interaction.channel.name.startswith("ticket-")
        ):
            if role.id == config.MOD_ROLE_ID:
                await interaction.response.send_message(
                    content="You can not remove the mod role from this ticket.",
                    ephemeral=True,
                )
            else:
                await interaction.channel.set_permissions(
                    role,
                    overwrite=discord.PermissionOverwrite(
                        read_messages=False,
                        send_messages=False,
                    ),
                )

                await interaction.response.send_message(
                    content=f"Removed {role.mention} from the ticket.",
                    allowed_mentions=discord.AllowedMentions.none(),
                )


async def setup(bot: commands.Bot):
    bot.tree.add_command(TicketCommands(name="ticket", description="ticket commands"))

    log.info("Added ticket commands")
