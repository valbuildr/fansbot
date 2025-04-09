from datetime import datetime
import discord
from discord.ext import commands
from typing import Callable
from typing import Optional


def dt_to_timestamp(dt: datetime, f: str = None) -> str:
    """Converts a datetime object to a Discord timestamp.

    Args:
        dt (datetime): The datetime object to convert.
        format (str): The format that the timestamp should be in. See the Discord Developer Documentation for more info: https://discord.com/developers/docs/reference#message-formatting-timestamp-styles

    Returns:
        str: The timestamp.
    """
    formats = ["d", "D", "t", "T", "f", "F", "R"]
    if f not in formats:
        return str(int(dt.timestamp()))
    else:
        return f"<t:{int(dt.timestamp())}:{f}>"


def epoch_to_datetime(epoch_time: str):
    if epoch_time.isnumeric():
        epoch_time = int(epoch_time)

        return datetime.fromtimestamp(epoch_time)
    else:
        raise Exception("Timestamp must be numeric.")


def format_interaction_msg(s: str, interaction: discord.Interaction):
    return (
        s.replace("{user_mention}", interaction.user.mention)
        .replace("{user_name}", interaction.user.name)
        .replace("{user_id}", str(interaction.user.id))
    )


def format_ctx_msg(s: str, ctx: commands.Context):
    return (
        s.replace("{user_mention}", ctx.author.mention)
        .replace("{user_name}", ctx.author.name)
        .replace("{user_id}", str(ctx.author.id))
    )


# credit to Hazzu on stackoverflow thanks mate (https://stackoverflow.com/a/76250596)
class Pagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            return False

    async def navegate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            if self.interaction.response.is_done():
                await self.interaction.followup.send(embed=emb)
            else:
                await self.interaction.response.send_message(embed=emb)
        elif self.total_pages > 1:
            self.update_buttons()
            if self.interaction.response.is_done():
                await self.interaction.followup.send(embed=emb, view=self)
            else:
                await self.interaction.response.send_message(embed=emb, view=self)

    async def edit_page(self, interaction: discord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(embed=emb, view=self)

    def update_buttons(self):
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        if self.index <= self.total_pages // 2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1
