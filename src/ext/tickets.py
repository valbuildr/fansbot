import discord
from discord.ext import commands
import config
from datetime import datetime
import utils


class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def send_ticket_msg(self, ctx: commands.Context):
        title = open("./src/data/ticket_title.txt", "r").read()
        description = open("./src/data/ticket_description.txt", "r").read()

        embed = discord.Embed(
            title=title, description=description, color=discord.Color.blurple()
        )

        ticket_channel = self.bot.get_guild(config.server_id).get_channel(
            config.ticket_channel_id
        )

        v = discord.ui.View()
        v.add_item(
            discord.ui.Button(
                label="Create Ticket",
                style=discord.ButtonStyle.primary,
                custom_id="create_ticket",
            )
        )

        await ticket_channel.send(embed=embed, view=v)

        await ctx.send("Ticket message sent!")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if (
                interaction.data["custom_id"] == "create_ticket"
                and interaction.data["component_type"] == 2
            ):
                ticket_channel = self.bot.get_guild(config.server_id).get_channel(
                    config.ticket_channel_id
                )

                tick = await ticket_channel.create_thread(
                    name=f"Ticket {utils.dt_to_timestamp(datetime.now(), 'a')}",
                    type=discord.ChannelType.private_thread,
                    invitable=True,
                )

                await tick.send(
                    content=f"{interaction.user.mention}, please describe your issue, and a staff member will be with you shortly.\n-# To close this ticket, simply close and/or lock the thread.\n-# <@&{config.mod_role_id}>"
                )

                await interaction.response.send_message(
                    content=f"Your ticket has been created in {tick.mention}.",
                    ephemeral=True,
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
