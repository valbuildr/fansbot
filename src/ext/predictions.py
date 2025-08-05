# TODO: Rename this file to economy.py when working on economy

import discord
from discord.ext import commands
from discord import app_commands as appcmds


class AutoPredictions(appcmds.Group):
    @appcmds.command(
        name="list", description="Mod/Helper: Lists all recurring predictions."
    )
    @appcmds.describe(
        title="Query by title",
        channel="Query by channel",
    )
    @appcmds.guild_only()
    async def _list(
        self,
        interaction: discord.Interaction,
        title: str = None,
        channel: discord.TextChannel = None,
    ): ...

    @appcmds.command(
        name="info",
        description="Mod/Helper: Gets information on a recurring prediction.",
    )
    @appcmds.describe(id="The ID of the auto-prediction to get info on.")
    @appcmds.guild_only()
    async def info(self, interaction: discord.Interaction, id: int): ...

    @appcmds.command(
        name="new",
        description="Mod/Helper: Creates a recurring prediction.",
    )
    # use a modal instead
    # @appcmds.describe(
    #     time="The time, in GMT, to create the prediction. (in HH:MM format)",
    #     monday="Whether or not to post the prediction on Mondays.",
    #     tuesday="Whether or not to post the prediction on Tuesdays.",
    #     wednesday="Whether or not to post the prediction on Wednesday.",
    #     thursday="Whether or not to post the prediction on Thursday.",
    #     friday="Whether or not to post the prediction on Fridays.",
    #     saturday="Whether or not to post the prediction on Saturdays.",
    #     sunday="Whether or not to post the prediction on Sundays.",
    #     end_on="The date to end this prediction. (in DD-MM-YYYY format)",
    #     duration="How long the prediction should run. (in DD:HH:MM format, max 7 days)",
    #     title="The title of the prediction.",
    #     options="The options in the prediction, seperated by \\. (ex: One\\Two)",
    #     channel="The channel to post the prediction and it's result.",
    #     enabled="Whether or not the prediction should be enabled when created.",
    # )
    @appcmds.guild_only()
    async def new(self, interaction: discord.Interaction): ...

    @appcmds.command(
        name="edit",
        description="Mod/Helper: Edits a recurring prediction.",
    )
    # use modal, see description for args on new()
    @appcmds.describe(id="The ID of the auto-prediction to edit.")
    @appcmds.guild_only()
    async def edit(self, interaction: discord.Interaction, id: int): ...

    @appcmds.command(
        name="delete",
        description="Mod/Helper: Deletes a recurring prediction.",
    )
    @appcmds.describe(id="The ID of the auto-prediction to delete.")
    @appcmds.guild_only()
    async def delete(self, interaction: discord.Interaction, id: int): ...


class Predictions(appcmds.Group):
    @appcmds.command(name="list", description="Lists all active predictions.")
    @appcmds.describe(
        title="Query by title",
        channel="Query by channel",
    )
    @appcmds.guild_only()
    async def _list(
        self,
        interaction: discord.Interaction,
        title: str = None,
        channel: discord.TextChannel = None,
    ): ...

    @appcmds.command(name="new", description="Mod/Helper: Creates a prediction.")
    # use a modal instead
    # @appcmds.describe(
    #     duration="How long the prediction should run. (in DD:HH:MM format, max 7 days)",
    #     title="The title of the prediction.",
    #     options="The options in the prediction, seperated by \\. (ex: One\\Two)",
    #     channel="The channel to post the prediction and it's result.",
    # )
    @appcmds.guild_only()
    async def new(self, interaction: discord.Interaction): ...

    @appcmds.command(name="edit", description="Mod/Helper: Edits a prediction.")
    # use modal, see description for args on new()
    @appcmds.describe(id="The ID of the prediction to edit.")
    @appcmds.guild_only()
    async def edit(self, interaction: discord.Interaction, id: int): ...

    @appcmds.command(
        name="end-voting", description="Mod/Helper: Ends voting on a prediction."
    )
    @appcmds.describe(id="The ID of the prediction to end voting on.")
    @appcmds.guild_only()
    async def end_voting(self, interaction: discord.Interaction, id: int): ...

    @appcmds.command(
        name="set-result", description="Mod/Helper: Sets the result of a prediction."
    )
    @appcmds.describe(
        id="The ID of the prediction to set the result on.",
        winner="The winning option.",
    )
    @appcmds.guild_only()
    async def set_result(
        self, interaction: discord.Interaction, id: int, winner: str
    ): ...


async def setup(bot: commands.Bot): ...
