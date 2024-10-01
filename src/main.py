import discord
import os
import config
from discord.ext import commands
from models.moderation import (
    ModerationNote,
    ModerationWarning,
    ModerationMute,
    ModerationKick,
    ModerationBan,
)
import database
from ext.moderation import bans, kicks, mutes, notes, warnings
import version

bot = commands.Bot(command_prefix="~", intents=discord.Intents.all())


if not os.path.exists("src/data"):
    os.makedirs("src/data")


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user.name}")
    database.db.create_tables(
        [
            ModerationNote,
            ModerationWarning,
            ModerationMute,
            ModerationKick,
            ModerationBan,
        ]
    )

    bans.add_commands(bot)
    kicks.add_commands(bot)
    mutes.add_commands(bot)
    notes.add_commands(bot)
    warnings.add_commands(bot)


@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == config.server_id:
        await member.add_roles(
            discord.Object(id=config.unverified_role_id)
        )


@bot.event
async def on_interaction(interaction: discord.Interaction) -> None:
    if interaction.type == discord.InteractionType.component:
        if (
            interaction.data["custom_id"] == "agree_to_rules"
            and interaction.data["component_type"] == 2
        ):
            member_role = bot.get_guild(config.server_id).get_role(
                config.member_role_id
            )
            if member_role not in interaction.user.roles:
                await interaction.user.add_roles(
                    discord.Object(id=config.member_role_id)
                )
                await interaction.user.remove_roles(
                    discord.Object(id=config.unverified_role_id)
                )

                await interaction.response.send_message(
                    content="Thanks for agreeing to the rules, I've added the member role to your profile.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    content="You already have the member role, so I haven't done anything.",
                    ephemeral=True,
                )


@bot.command(hidden=True)
@commands.guild_only()
async def rule_agreement_button(ctx: commands.Context) -> None:
    channel = bot.get_guild(config.server_id).get_channel(config.rules_channel_id)
    mod_role = bot.get_guild(config.server_id).get_role(config.mod_role_id)

    if mod_role in ctx.author.roles:
        v = discord.ui.View(timeout=None)
        b = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label="I agree!",
            custom_id="agree_to_rules",
        )
        v.add_item(b)

        await channel.send(view=v)


@bot.command()
@commands.is_owner()
@commands.dm_only()
async def sync(ctx: commands.Context) -> None:
    r = await ctx.send(content="Syncing...")
    await bot.tree.sync()
    await r.edit(content="Synced!")


@bot.tree.command(name="rules", description="Gets the server rules!")
@discord.app_commands.guild_only()
async def rules(interaction: discord.Interaction) -> None:
    msg = (
        await bot.get_guild(config.server_id)
        .get_channel(config.rules_channel_id)
        .fetch_message(config.rules_message_id)
    )

    msg = msg.content.split("\n")
    msg.pop()
    msg.pop()
    msg.pop()
    content = ""
    for line in msg:
        content = content + f"{line}\n"

    await interaction.response.send_message(
        content=content, ephemeral=True, suppress_embeds=True
    )


@bot.command(name="version")
async def v(ctx: commands.Context) -> None:
    await ctx.send(
        content=f"*Version {version.version}*\n*Source code: {version.source_code_link}*"
    )






@bot.hybrid_group(name="convert")
async def convert(ctx: commands.Context) -> None:
    if ctx.invoked_subcommand == None:
        await ctx.send(f"Please proivde a valid subcommand.\nFor a list of valid subcommands, run `{bot.command_prefix}help {ctx.command.name}`")


@convert.command(
        name="area",
        description="Convert a unit of area."
)
@discord.app_commands.choices(
    unit_from=[
        discord.app_commands.Choice(name="Square kilometer (km²)", value="sqkm"),
        discord.app_commands.Choice(name="Square meter (m²)", value="sqm"),
        discord.app_commands.Choice(name="Square mile (mi²)", value="sqmi"),
        discord.app_commands.Choice(name="Square yard (yd²)", value="sqyd"),
        discord.app_commands.Choice(name="Square foot (ft²)", value="sqft"),
        discord.app_commands.Choice(name="Square inch (in²)", value="sqin"),
        discord.app_commands.Choice(name="Hectare (ha)", value="ha"),
        discord.app_commands.Choice(name="Acre (ac)", value="ac"),
    ],
    unit_to=[
        discord.app_commands.Choice(name="Square kilometer (km²)", value="sqkm"),
        discord.app_commands.Choice(name="Square meter (m²)", value="sqm"),
        discord.app_commands.Choice(name="Square mile (mi²)", value="sqmi"),
        discord.app_commands.Choice(name="Square yard (yd²)", value="sqyd"),
        discord.app_commands.Choice(name="Square foot (ft²)", value="sqft"),
        discord.app_commands.Choice(name="Square inch (in²)", value="sqin"),
        discord.app_commands.Choice(name="Hectare (ha)", value="ha"),
        discord.app_commands.Choice(name="Acre (ac)", value="ac"),
    ]
)
@discord.app_commands.describe(
    input="The number of units to convert.",
    unit_from="The unit to convet from.",
    unit_to="The unit to convet to.",
)
async def convert_area(ctx: commands.Context, input: float, unit_from: str, unit_to: str):
    descriptions = {
        "sqkm": "km²",
        "sqm": "m²",
        "sqmi": "mi²",
        "sqyd": "yd²",
        "sqft": "ft²",
        "sqin": "in²",
        "ha": "ha",
        "ac": "ac",
    }
    
    conversion_factors = {
        "km²": 1e6,            # Square kilometers
        "m²": 1,               # Square meters (base unit)
        "mi²": 2.58998811e6,   # Square miles
        "yd²": 0.83612736,     # Square yards
        "ft²": 0.09290304,     # Square feet
        "in²": 0.00064516,     # Square inches
        "ha": 10000,           # Hectares
        "ac": 4046.856422      # Acres
    }

    # Check if units are valid
    if unit_from.lower() not in descriptions or unit_to.lower() not in descriptions:
        await ctx.send(f"Invalid unit(s). Please use: {', '.join(descriptions.keys())}")
        return

    # Convert the value
    converted_value = input * conversion_factors[descriptions[unit_from.lower()]] / conversion_factors[descriptions[unit_to.lower()]]

    # Send the response
    await ctx.send(f"{input} {descriptions[unit_from.lower()]} is equal to {converted_value:.2f} {descriptions[unit_to.lower()]}")


@convert.command(
        name="data-transfer",
        description="Convert a rate of a data transfer."
)
@discord.app_commands.choices(
    unit_from=[
        discord.app_commands.Choice(name="Bit per second (b/s)", value="byte"),
        discord.app_commands.Choice(name="Kilobit per second (kb/s)", value="kilobit"),
        discord.app_commands.Choice(name="Kilobyte per second (kB/s)", value="kilobyte"),
        discord.app_commands.Choice(name="Kibibit per second (Kib/s)", value="kibibit"),
        discord.app_commands.Choice(name="Megabit per second (Mb/s)", value="megabit"),
        discord.app_commands.Choice(name="Megabyte per second (MB/s)", value="megabyte"),
        discord.app_commands.Choice(name="Mebibit per second (MiB/s)", value="mebibit"),
        discord.app_commands.Choice(name="Gigabit per second (Gb/s)", value="gigabit"),
        discord.app_commands.Choice(name="Gigabyte per second (GB/s)", value="gigabyte"),
        discord.app_commands.Choice(name="Gibibit per second (GiB/s)", value="gibibit"),
        discord.app_commands.Choice(name="Terabit per second (Tb/s)", value="terabit"),
        discord.app_commands.Choice(name="Terabyte per second (TB/s)", value="terabyte"),
        discord.app_commands.Choice(name="Tebibit per second (TiB/s)", value="tebibit"),
    ],
    unit_to=[
        discord.app_commands.Choice(name="Bit per second (b/s)", value="byte"),
        discord.app_commands.Choice(name="Kilobit per second (kb/s)", value="kilobit"),
        discord.app_commands.Choice(name="Kilobyte per second (kB/s)", value="kilobyte"),
        discord.app_commands.Choice(name="Kibibit per second (Kib/s)", value="kibibit"),
        discord.app_commands.Choice(name="Megabit per second (Mb/s)", value="megabit"),
        discord.app_commands.Choice(name="Megabyte per second (MB/s)", value="megabyte"),
        discord.app_commands.Choice(name="Mebibit per second (MiB/s)", value="mebibit"),
        discord.app_commands.Choice(name="Gigabit per second (Gb/s)", value="gigabit"),
        discord.app_commands.Choice(name="Gigabyte per second (GB/s)", value="gigabyte"),
        discord.app_commands.Choice(name="Gibibit per second (GiB/s)", value="gibibit"),
        discord.app_commands.Choice(name="Terabit per second (Tb/s)", value="terabit"),
        discord.app_commands.Choice(name="Terabyte per second (TB/s)", value="terabyte"),
        discord.app_commands.Choice(name="Tebibit per second (TiB/s)", value="tebibit"),
    ]
)
@discord.app_commands.describe(
    input="The number of units to convert.",
    unit_from="The unit to convet from.",
    unit_to="The unit to convet to.",
)
async def convert_data_transfer_rate(ctx: commands.Context, input: float, unit_from: str, unit_to: str):
    descriptions = {
        "byte": "b/s",
        "kilobit": "kb/s",
        "kilobyte": "kB/s",
        "kibibit": "Kib/s",
        "megabit": "Mb/s",
        "megabyte": "MB/s",
        "mebibit": "MiB/s",
        "gigabit": "Gb/s",
        "gigabyte": "GB/s",
        "gibibit": "GiB/s",
        "terabit": "Tb/s",
        "terabyte": "TB/s",
        "tebibit": "TiB/s",
    }
    
    conversion_factors = {
        "b/s": 1,
        "kb/s": 1000,
        "kB/s": 1000 * 8,
        "Kib/s": 1024,
        "Mb/s": 1000000,
        "MB/s": 1000000 * 8,
        "MiB/s": 1024 * 1024,
        "Gb/s": 1000000000,
        "GB/s": 1000000000 * 8,
        "GiB/s": 1024 * 1024 * 1024,
        "Tb/s": 1000000000000,
        "TB/s": 1000000000000 * 8,
        "TiB/s": 1024 * 1024 * 1024 * 1024
    }

    # Check if units are valid
    if unit_from.lower() not in descriptions or unit_to.lower() not in descriptions:
        await ctx.send(f"Invalid unit(s). Please use: {', '.join(descriptions.keys())}")
        return

    # Convert the value
    converted_value = input * conversion_factors[descriptions[unit_from.lower()]] / conversion_factors[descriptions[unit_to.lower()]]

    # Send the response
    await ctx.send(f"{input} {descriptions[unit_from.lower()]} is equal to {converted_value:.2f} {descriptions[unit_to.lower()]}")


@convert.command(
        name="digital-storage",
        description="Convert size of data."
)
@discord.app_commands.choices(
    unit_from=[
        discord.app_commands.Choice(name="Bit", value="b"),
        discord.app_commands.Choice(name="Kilobit", value="kb"),
        discord.app_commands.Choice(name="Kibibit", value="KiB"),
        discord.app_commands.Choice(name="Megabit", value="Mb"),
        discord.app_commands.Choice(name="Mebibit", value="MiB"),
        discord.app_commands.Choice(name="Gigabit", value="Gb"),
        discord.app_commands.Choice(name="Gibibit", value="GiB"),
        discord.app_commands.Choice(name="Terabit", value="Tb"),
        discord.app_commands.Choice(name="Tebibit", value="TiB"),
        discord.app_commands.Choice(name="Petabit", value="Pb"),
        discord.app_commands.Choice(name="Pebibit", value="PiB"),
        discord.app_commands.Choice(name="Byte", value="B"),
        discord.app_commands.Choice(name="Kilobyte", value="kB"),
        discord.app_commands.Choice(name="Kibibyte", value="KiB"),
        discord.app_commands.Choice(name="Megabyte", value="MB"),
        discord.app_commands.Choice(name="Mebibyte", value="MiB"),
        discord.app_commands.Choice(name="Gigabyte", value="GB"),
        discord.app_commands.Choice(name="Gibibyte", value="GiB"),
        discord.app_commands.Choice(name="Terabyte", value="TB"),
        discord.app_commands.Choice(name="Tebibit", value="TiB"),
        discord.app_commands.Choice(name="Petabyte", value="PB"),
        discord.app_commands.Choice(name="Pebibyte", value="PiB"),
    ],
    unit_to=[
        discord.app_commands.Choice(name="Bit", value="b"),
        discord.app_commands.Choice(name="Kilobit", value="kb"),
        discord.app_commands.Choice(name="Kibibit", value="KiB"),
        discord.app_commands.Choice(name="Megabit", value="Mb"),
        discord.app_commands.Choice(name="Mebibit", value="MiB"),
        discord.app_commands.Choice(name="Gigabit", value="Gb"),
        discord.app_commands.Choice(name="Gibibit", value="GiB"),
        discord.app_commands.Choice(name="Terabit", value="Tb"),
        discord.app_commands.Choice(name="Tebibit", value="TiB"),
        discord.app_commands.Choice(name="Petabit", value="Pb"),
        discord.app_commands.Choice(name="Pebibit", value="PiB"),
        discord.app_commands.Choice(name="Byte", value="B"),
        discord.app_commands.Choice(name="Kilobyte", value="kB"),
        discord.app_commands.Choice(name="Kibibyte", value="KiB"),
        discord.app_commands.Choice(name="Megabyte", value="MB"),
        discord.app_commands.Choice(name="Mebibyte", value="MiB"),
        discord.app_commands.Choice(name="Gigabyte", value="GB"),
        discord.app_commands.Choice(name="Gibibyte", value="GiB"),
        discord.app_commands.Choice(name="Terabyte", value="TB"),
        discord.app_commands.Choice(name="Tebibit", value="TiB"),
        discord.app_commands.Choice(name="Petabyte", value="PB"),
        discord.app_commands.Choice(name="Pebibyte", value="PiB"),
    ]
)
@discord.app_commands.describe(
    input="The number of units to convert.",
    unit_from="The unit to convet from.",
    unit_to="The unit to convet to.",
)
async def convert_digital_storage(ctx: commands.Context, input: float, unit_from: str, unit_to: str):
    descriptions = {
        "bit": "b",
        "kilobit": "kb",
        "kibibit": "KiB",
        "megabit": "Mb",
        "mebibit": "MiB",
        "gigabit": "Gb",
        "gibibit": "GiB",
        "terabit": "Tb",
        "tebibit": "TiB",
        "petabit": "Pb",
        "pebibit": "PiB",
        "byte": "B",
        "kilobyte": "kB",
        "kibibyte": "KiB",
        "megabyte": "MB",
        "mebibyte": "MiB",
        "gigabyte": "GB",
        "gibibyte": "GiB",
        "terabyte": "TB",
        "tebibit": "TiB",
        "petabyte": "PB",
        "pebibyte": "PiB",
    }
    
    conversion_factors = {
        "b": 1,
        "kb": 1000,
        "Kib": 1024,
        "Mb": 1000000,
        "MiB": 1024 * 1024,
        "Gb": 1000000000,
        "GiB": 1024 * 1024 * 1024,
        "Tb": 1000000000000,
        "TiB": 1024 * 1024 * 1024 * 1024,
        "Pb": 1000000000000000,
        "PiB": 1024 * 1024 * 1024 * 1024 * 1024,
        "B": 8,
        "kB": 1000 * 8,
        "KiB": 1024 * 8,
        "MB": 1000000 * 8,
        "MiB": 1024 * 1024 * 8,
        "GB": 1000000000 * 8,
        "GiB": 1024 * 1024 * 1024 * 8,
        "TB": 1000000000000 * 8,
        "TiB": 1024 * 1024 * 1024 * 1024 * 8,
        "PB": 1000000000000000 * 8,
        "PiB": 1024 * 1024 * 1024 * 1024 * 1024 * 8
    }

    # Check if units are valid
    if unit_from.lower() not in descriptions or unit_to.lower() not in descriptions:
        await ctx.send(f"Invalid unit(s). Please use: {', '.join(descriptions.keys())}")
        return

    # Convert the value
    converted_value = input * conversion_factors[descriptions[unit_from.lower()]] / conversion_factors[descriptions[unit_to.lower()]]

    # Send the response
    await ctx.send(f"{input} {descriptions[unit_from.lower()]} is equal to {converted_value:.2f} {descriptions[unit_to.lower()]}")


# TODO: Engery


# TODO: Frequency


# TODO: Fuel Economy


# TODO: Length


# TODO: Mass


# TODO: Plane Angle


# TODO: Speed


@convert.command(
        name="temperature",
        description="Convert a unit of temperature measurement."
)
@discord.app_commands.choices(
    unit_from=[
        discord.app_commands.Choice(name="Celsius", value="c"),
        discord.app_commands.Choice(name="Fahrenheit", value="f"),
        discord.app_commands.Choice(name="Kelvin", value="k"),
    ],
    unit_to=[
        discord.app_commands.Choice(name="Celsius", value="c"),
        discord.app_commands.Choice(name="Fahrenheit", value="f"),
        discord.app_commands.Choice(name="Kelvin", value="k"),
    ]
)
@discord.app_commands.describe(
    input="The number of units to convert.",
    unit_from="The unit to convet from.",
    unit_to="The unit to convet to.",
)
async def convert_temperature(ctx: commands.Context, input: float, unit_from: str, unit_to: str):
    descriptions = {
        "celsius": "C",
        "fahrenheit": "F",
        "kelvin": "K",
        "c": "C",
        "f": "F",
        "k": "K"
    }
    
    conversion_factors = {
        "C": 1,
        "F": 9/5,
        "K": 1
    }

    conversion_offsets = {
        "C": 0,
        "F": 32,
        "K": 273.15
    }

    # Check if units are valid
    if unit_from.lower() not in descriptions or unit_to.lower() not in descriptions:
        await ctx.send(f"Invalid unit(s). Please use: {', '.join(descriptions.keys())}")
        return

    # Convert the value
    converted_value = (input + conversion_offsets[descriptions[unit_from.lower()]]) * conversion_factors[descriptions[unit_from.lower()]] / conversion_factors[descriptions[unit_to.lower()]] - conversion_offsets[descriptions[unit_to.lower()]]

    # Send the response
    await ctx.send(f"{input} {descriptions[unit_from.lower()]} is equal to {converted_value:.2f} {descriptions[unit_to.lower()]}")


# TODO: Time


@convert.command(
        name="volume",
        description="Convert units of volume."
)
@discord.app_commands.choices(
    unit_from=[
        discord.app_commands.Choice(name="US gallon", value="usgal"),
        discord.app_commands.Choice(name="US quart", value="usqt"),
        discord.app_commands.Choice(name="US pint", value="uspt"),
        discord.app_commands.Choice(name="US cup", value="uscup"),
        discord.app_commands.Choice(name="US fluid ounce", value="usfloz"),
        discord.app_commands.Choice(name="US tablespoon", value="ustbsp"),
        discord.app_commands.Choice(name="US teaspoon", value="ustsp"),
        discord.app_commands.Choice(name="Cubic meter", value="m3"),
        discord.app_commands.Choice(name="Litre/Liter", value="l3"),
        discord.app_commands.Choice(name="Mililitre/Mililiter", value="ml"),
        discord.app_commands.Choice(name="Imperial gallon", value="impgal"),
        discord.app_commands.Choice(name="Imperial quart", value="impqt"),
        discord.app_commands.Choice(name="Imperial pint", value="imppt"),
        discord.app_commands.Choice(name="Imperial cup", value="impcup"),
        discord.app_commands.Choice(name="Imperial fluid ounce", value="impfloz"),
        discord.app_commands.Choice(name="Imperial tablespoon", value="imptbsp"),
        discord.app_commands.Choice(name="Imperial teaspoon", value="imptsp"),
        discord.app_commands.Choice(name="Cubic foot", value="ft3"),
        discord.app_commands.Choice(name="Cubic inch", value="in3"),
    ],
    unit_to=[
        discord.app_commands.Choice(name="US gallon", value="usgal"),
        discord.app_commands.Choice(name="US quart", value="usqt"),
        discord.app_commands.Choice(name="US pint", value="uspt"),
        discord.app_commands.Choice(name="US cup", value="uscup"),
        discord.app_commands.Choice(name="US fluid ounce", value="usfloz"),
        discord.app_commands.Choice(name="US tablespoon", value="ustbsp"),
        discord.app_commands.Choice(name="US teaspoon", value="ustsp"),
        discord.app_commands.Choice(name="Cubic meter", value="m3"),
        discord.app_commands.Choice(name="Litre/Liter", value="l"),
        discord.app_commands.Choice(name="Mililitre/Mililiter", value="ml"),
        discord.app_commands.Choice(name="Imperial gallon", value="impgal"),
        discord.app_commands.Choice(name="Imperial quart", value="impqt"),
        discord.app_commands.Choice(name="Imperial pint", value="imppt"),
        discord.app_commands.Choice(name="Imperial cup", value="impcup"),
        discord.app_commands.Choice(name="Imperial fluid ounce", value="impfloz"),
        discord.app_commands.Choice(name="Imperial tablespoon", value="imptbsp"),
        discord.app_commands.Choice(name="Imperial teaspoon", value="imptsp"),
        discord.app_commands.Choice(name="Cubic foot", value="ft3"),
        discord.app_commands.Choice(name="Cubic inch", value="in3"),
    ]
)
@discord.app_commands.describe(
    input="The number of units to convert.",
    unit_from="The unit to convet from.",
    unit_to="The unit to convet to.",
)
async def convert_digital_storage(ctx: commands.Context, input: float, unit_from: str, unit_to: str):
    descriptions = {
        "usgal": "US gal",
        "usqt": "US qt",
        "uspt": "US pt",
        "uscup": "US cup",
        "usfloz": "US fl oz",
        "ustbsp": "US tbsp",
        "ustsp": "US tsp",
        "m3": "m³",
        "l": "L",
        "ml": "mL",
        "impgal": "imp gal",
        "impqt": "imp qt",
        "imppt": "imp pt",
        "impcup": "imp cup",
        "impfloz": "imp fl oz",
        "imptbsp": "imp tbsp",
        "imptsp": "imp tsp",
        "ft3": "ft³",
        "in3": "in³",
    }
    
    conversion_factors = {
        "US gal": 3.785411784,  # US liquid gallons
        "US qt": 0.946352946,   # US liquid quarts
        "US pt": 0.473176473,   # US liquid pints
        "US cup": 0.236588237,  # US legal cups
        "US fl oz": 0.029573529, # US fluid ounces
        "US tbsp": 0.014786765, # US tablespoons
        "US tsp": 0.004928922,  # US teaspoons
        "m³": 1,                   # Cubic meters
        "L": 0.001,                # Liters
        "mL": 0.000001,             # Milliliters
        "imp gal": 4.54609,        # Imperial gallons
        "imp qt": 1.13696,         # Imperial quarts
        "imp pt": 0.56848,         # Imperial pints
        "imp cup": 0.28413,        # Imperial cups
        "imp fl oz": 0.028413,     # Imperial fluid ounces
        "imp tbsp": 0.014207,     # Imperial tablespoons
        "imp tsp": 0.004736,      # Imperial teaspoons
        "ft³": 0.028317,           # Cubic feet
        "in³": 0.000016387
    }

    # Check if units are valid
    if unit_from.lower() not in descriptions or unit_to.lower() not in descriptions:
        await ctx.send(f"Invalid unit(s). Please use: {', '.join(descriptions.keys())}")
        return

    # Convert the value
    converted_value = input * conversion_factors[descriptions[unit_from.lower()]] / conversion_factors[descriptions[unit_to.lower()]]

    # Send the response
    await ctx.send(f"{input} {descriptions[unit_from.lower()]} is equal to {converted_value:.2f} {descriptions[unit_to.lower()]}")






bot.run(config.discord_token)
