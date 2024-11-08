import discord
from discord.ext import commands
from discord import app_commands as appcmds


area_units = [
    appcmds.Choice(name="Square kilometer", value="sq km"),
    appcmds.Choice(name="Square meter", value="sq m"),
    appcmds.Choice(name="Square mile", value="sq mi"),
    appcmds.Choice(name="Square yard", value="sq yd"),
    appcmds.Choice(name="Square foot", value="sq ft"),
    appcmds.Choice(name="Square inch", value="sq in"),
    appcmds.Choice(name="Hectare", value="h"),
    appcmds.Choice(name="Acre", value="a"),
]

dtr_units = [
    appcmds.Choice(name="Bit per second", value="Bit"),
    appcmds.Choice(name="Kilobit per second", value="Kilobit"),
    appcmds.Choice(name="Kilobyte per second", value="Kilobyte"),
    appcmds.Choice(name="Kibibit per second", value="Kibibit"),
    appcmds.Choice(name="Megabit per second", value="Megabit"),
    appcmds.Choice(name="Megabyte per second", value="Megabyte"),
    appcmds.Choice(name="Mebibit per second", value="Mebibit"),
    appcmds.Choice(name="Gigabit per second", value="Gigabit"),
    appcmds.Choice(name="Gigabyte per second", value="Gigabyte"),
    appcmds.Choice(name="Gibibit per second", value="Gibibit"),
    appcmds.Choice(name="Terabit per second", value="Terabit"),
    appcmds.Choice(name="Terabyte per second", value="Terabyte"),
    appcmds.Choice(name="Tebibit per second", value="Tebibit"),
]


class ConversionCommands(appcmds.Group):
    @appcmds.command(name="area", description="Convert units of area.")
    @appcmds.describe(
        unit_from="The unit do convert from.",
        unit_to="The unit to convert to.",
        val_from="The number of units to convert from.",
    )
    @appcmds.choices(
        unit_from=area_units,
        unit_to=area_units,
    )
    async def area(
        self,
        interaction: discord.Interaction,
        unit_from: str,
        unit_to: str,
        val_from: int,
    ): ...

    @appcmds.command(
        name="data-transfer-rate", description="Convert units of data transfer rate."
    )
    @appcmds.describe(
        unit_from="The unit do convert from.",
        unit_to="The unit to convert to.",
        val_from="The number of units to convert from.",
    )
    @appcmds.choices(
        unit_from=dtr_units,
        unit_to=dtr_units,
    )
    async def dtr(
        self,
        interaction: discord.Interaction,
        unit_from: str,
        unit_to: str,
        val_from: int,
    ): ...


async def setup(bot: commands.Bot):
    bot.add_command(
        ConversionCommands(name="convert", description="Conversion commands")
    )
