import discord
from discord.ext import commands
from models.economy import Economy, WorkReplies
import random
import config


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="create-bank-account", description="Create a bank account.")
    async def create_bank_account(self, ctx: commands.Context):
        u = Economy.fetch(ctx.author.id)

        if u.has_bank_account:
            await ctx.send(
                content=f"You already have a bank account.\n-# Use `{self.bot.command_prefix}deposit` to deposit money and `{self.bot.command_prefix}withdraw` to withdraw money."
            )
        else:
            u.has_bank_account = True
            u.bank = 0
            u.save()
            await ctx.send(
                content=f"You've created a bank account!\nUse `{self.bot.command_prefix}deposit` to deposit money and `{self.bot.command_prefix}withdraw` to withdraw money."
            )

    @commands.command(name="close-bank-account", description="Create a bank account.")
    async def close_bank_account(self, ctx: commands.Context):
        u = Economy.fetch(ctx.author.id)

        if u.has_bank_account:
            u.has_bank_account = False
            u.cash += u.bank
            u.bank = 0
            u.save()

            await ctx.send(
                content=f"You've closed your bank account.\nAll money you had in your bank account has been moved to your cash balance."
            )
        else:
            await ctx.send(
                content=f"You don't have a bank account!\n-# Use `{self.bot.command_prefix}create-bank-account` to start one."
            )

    @commands.command(name="add-work-reply", description="(MOD ONLY) Add a work reply.")
    @commands.has_role(config.mod_role_id)
    async def add_work_reply(self, ctx: commands.Context, *reply: str):
        reply = " ".join(reply)

        if "{}" in reply:
            a = WorkReplies.create(text=reply)

            await ctx.send(content=f"Created work reply {a.id}.")
        else:
            await ctx.send(
                content="Please provide an empty spot with `{}` to put the amount of money earned."
            )

    @commands.command(name="work", description="Make some cash!")
    async def work(self, ctx: commands.Context):
        amount = random.randint(50, 500)

        r = random.choice(WorkReplies.get_all())

        reply = r.text.format(amount)

        u = Economy.fetch(ctx.author.id)
        u.cash += amount
        u.save()

        await ctx.send(content=f"{reply}\n-# Reply #{r.id}")

    @commands.command(name="balance", description="Get a balance.", aliases=["bal"])
    async def balance(self, ctx: commands.Context, user: discord.User = None):
        if user:
            u = Economy.fetch(user.id)

            e = discord.Embed(title=f"{user.name}'s Balance")

            e.add_field(name="Cash", value=u.cash)
            if u.has_bank_account:
                e.add_field(name="Bank", value=u.bank)

            await ctx.send(embed=e)
        else:
            u = Economy.fetch(ctx.author.id)

            e = discord.Embed(title=f"{ctx.author.name}'s Balance")

            e.add_field(name="Cash", value=u.cash)
            if u.has_bank_account:
                e.add_field(name="Bank", value=u.bank)

            await ctx.send(embed=e)

    @commands.command(
        name="deposit",
        description="Deposit money into the bank, if you have an account.",
        aliases=["dep"],
    )
    async def deposit(self, ctx: commands.Context, val: int):
        u = Economy.fetch(ctx.author.id)

        if u.has_bank_account:
            if val > u.cash:
                await ctx.send(content="You don't have that much cash!")
            else:
                u.cash -= val
                u.bank += val
                u.save()

                await ctx.send(content=f"Deposited {val}.")
        else:
            await ctx.send(
                content=f"You don't have a bank account! Start one by running `{self.bot.command_prefix}create-bank-account`."
            )

    @commands.command(
        name="withdraw",
        description="Withdraw money from the bank, if you have an account.",
        aliases=["wd"],
    )
    async def deposit(self, ctx: commands.Context, val: int):
        u = Economy.fetch(ctx.author.id)

        if u.has_bank_account:
            if val > u.bank:
                await ctx.send(content="You don't have that much money in the bank!")
            else:
                u.cash += val
                u.bank -= val
                u.save()

                await ctx.send(content=f"Withdrew {val}.")
        else:
            await ctx.send(
                content=f"You don't have a bank account! Start one by running `{self.bot.command_prefix}create-bank-account`."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
