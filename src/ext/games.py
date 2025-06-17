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


@appcmds.command(
    name="blackjack", description="Play a game of blackjack. (Not for money!)"
)
async def blackjack(interaction: discord.Interaction):
    # Simple blackjack implementation
    cards = [
        "A",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
    ]
    deck = cards * 4
    random.shuffle(deck)

    def card_value(card):
        if card in ["J", "Q", "K"]:
            return 10
        if card == "A":
            return 11
        return int(card)

    def hand_value(hand):
        value = sum(card_value(card) for card in hand)
        # Adjust for Aces
        aces = hand.count("A")
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    embed = discord.Embed(
        title="Blackjack",
        description=f"Your hand: {', '.join(player_hand)} (Total: {hand_value(player_hand)})\n"
        f"Dealer shows: {dealer_hand[0]}",
        color=discord.Color.green(),
    )
    view = discord.ui.View()

    async def end_game(msg, win):
        result = "You win!" if win else "You lose!" if win is False else "It's a tie!"
        embed.description += f"\n\n**{result}**\nDealer's hand: {', '.join(dealer_hand)} (Total: {hand_value(dealer_hand)})"
        for child in view.children:
            child.disabled = True
        await msg.edit(embed=embed, view=view)

    class HitButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Hit", style=discord.ButtonStyle.primary)

        async def callback(self, interaction2: discord.Interaction):
            if interaction2.user != interaction.user:
                await interaction2.response.send_message(
                    "This isn't your game.", ephemeral=True
                )
                return
            player_hand.append(deck.pop())
            val = hand_value(player_hand)
            embed.description = f"Your hand: {', '.join(player_hand)} (Total: {val})\nDealer shows: {dealer_hand[0]}"
            if val > 21:
                await end_game(msg, False)
            else:
                await msg.edit(embed=embed, view=view)
            await interaction2.response.defer()

    class StandButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Stand", style=discord.ButtonStyle.secondary)

        async def callback(self, interaction2: discord.Interaction):
            if interaction2.user != interaction.user:
                await interaction2.response.send_message(
                    "This isn't your game.", ephemeral=True
                )
                return
            # Dealer's turn
            while hand_value(dealer_hand) < 17:
                dealer_hand.append(deck.pop())
            player_val = hand_value(player_hand)
            dealer_val = hand_value(dealer_hand)
            if dealer_val > 21 or player_val > dealer_val:
                await end_game(msg, True)
            elif player_val < dealer_val:
                await end_game(msg, False)
            else:
                await end_game(msg, None)
            await interaction2.response.defer()

    view.add_item(HitButton())
    view.add_item(StandButton())

    await interaction.response.send_message(embed=embed, view=view)
    msg = await interaction.original_response()


async def setup(bot: commands.Bot):
    bot.tree.add_command(coin_flip)
    bot.tree.add_command(roll_dice)
    bot.tree.add_command(PickOneCommand(name="pick", description="Pick commands"))
    bot.tree.add_command(blackjack)
