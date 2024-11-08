import discord
from discord.ext import commands


class ConversionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="convert", description="Convert group")
    async def convert(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply(
                content=f"Please specify a subcommand. To see a list of subcommands, run `{self.bot.command_prefix}convert help"
            )

    @convert.command(
        name="help", description="Lists all subcommands of the convert group."
    )
    async def help(self, ctx: commands.Context): ...

    @convert.command(name="area", description="Convert a unit of area.")
    async def area(self, ctx: commands.Context): ...


async def setup(bot: commands.Bot):
    await bot.add_cog(ConversionCog(bot))
