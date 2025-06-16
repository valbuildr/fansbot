import discord
from discord import app_commands as appcmds
from discord.ext import commands
import random


@appcmds.command(name="coin-flip", description="Flip a coin.")
async def coin_flip(interaction: discord.Interaction):
    r = random.randint(0, 1)
    if r == 1:
        await interaction.response.send_message(content="I choose `Heads`.")
    else:
        await interaction.response.send_message(content="I choose `Tails`.")


@appcmds.command(name="roll-dice", description="Roll a dice.")
@appcmds.choices(
    type=[
        appcmds.Choice(name="D4", value=4),
        appcmds.Choice(name="D6 (default)", value=6),
        appcmds.Choice(name="D8", value=8),
        appcmds.Choice(name="D10", value=10),
        appcmds.Choice(name="D12", value=12),
        appcmds.Choice(name="D20", value=20),
    ]
)
@appcmds.describe(type="The type of dice to roll.")
async def roll_dice(interaction: discord.Interaction, type: int = 6):
    r = random.randint(1, type)
    await interaction.response.send_message(content=f"I choose `{r}`.")


class PickOneCommand(appcmds.Group):
    @appcmds.command(
        name="list", description="Randomly choose an item from the provided list."
    )
    @appcmds.describe(list="The list to pick from. Seperate entries by \\.")
    async def l(self, interaction: discord.Interaction, list: str):
        r = random.choice(list.split("\\"))
        await interaction.response.send_message(content=f"I choose `{r}`.")

    @appcmds.command(
        name="number", description="Randomly choose a number from the provided range."
    )
    @appcmds.describe(
        min="The minimum number to pick. Defaults to 1.",
        max="The maximum number to pick.",
    )
    async def number(self, interaction: discord.Interaction, max: int, min: int = 1):
        r = random.randint(min, max)
        await interaction.response.send_message(content=f"I choose `{r}`.")


async def setup(bot: commands.Bot):
    bot.tree.add_command(coin_flip)
    bot.tree.add_command(roll_dice)
    bot.tree.add_command(PickOneCommand(name="pick", description="Pick commands"))
