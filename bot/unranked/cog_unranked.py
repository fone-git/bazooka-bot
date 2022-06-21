import discord
from discord.ext import commands
from opylib import db_cache

from bot.common.cog_common import CogCommon
from bot.common.player import Player
from bot.unranked.unranked import Unranked
from conf import Conf, DBKeys

conf = Conf.Unranked
"""Map class with setting for this cog to variable"""


class CogUnranked(CogCommon, name='Unranked'):
    data: Unranked  # Specify type of attribute for linting

    def __init__(self, db: db_cache):
        super().__init__(db, conf=conf, db_key=DBKeys.UNRANKED,
                         data_def_constructor=Unranked)

    ##########################################################################
    # BASE GROUP
    @commands.group(**conf.BASE_GROUP)
    async def base(self, ctx):
        await super().base(ctx)

    ##########################################################################
    # NORMAL COMMANDS
    @base.command(**conf.Command.SCORE)
    async def score(self, ctx, score: int):
        await self.score_other(ctx, ctx.author, score)

    @base.command(**conf.Command.DISPLAY)
    async def display(self, ctx):
        await self.send_data_str(ctx)

    @base.command(**conf.Command.REMOVE)
    async def remove(self, ctx):
        await self.remove_other(ctx, ctx.author)

    ##########################################################################
    # CONVENIENCE COMMANDS TO FACILITATE FREQUENT USE CASE
    @base.command(**conf.Command.ONE)
    async def one(self, ctx):
        await self.score_other(ctx, ctx.author, 1)

    @base.command(**conf.Command.TWO)
    async def two(self, ctx):
        await self.score_other(ctx, ctx.author, 2)

    @base.command(**conf.Command.THREE)
    async def three(self, ctx):
        await self.score_other(ctx, ctx.author, 3)

    @base.command(**conf.Command.FOUR)
    async def four(self, ctx):
        await self.score_other(ctx, ctx.author, 4)

    @base.command(**conf.Command.FIVE)
    async def five(self, ctx):
        await self.score_other(ctx, ctx.author, 5)

    @base.command(**conf.Command.SIX)
    async def six(self, ctx):
        await self.score_other(ctx, ctx.author, 6)

    @base.command(**conf.Command.SEVEN)
    async def seven(self, ctx):
        await self.score_other(ctx, ctx.author, 7)

    @base.command(**conf.Command.EIGHT)
    async def eight(self, ctx):
        await self.score_other(ctx, ctx.author, 8)

    @base.command(**conf.Command.NINE)
    async def nine(self, ctx):
        await self.score_other(ctx, ctx.author, 9)

    @base.command(**conf.Command.TEN)
    async def ten(self, ctx):
        await self.score_other(ctx, ctx.author, 10)

    ##########################################################################
    # PRIVILEGED COMMANDS
    @base.command(**conf.Command.RESET)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def reset(self, ctx, confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data = self.data_def_constructor()
        self.save()
        await ctx.send("Unranked Reset")

    @base.command(**conf.Command.SCORE_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def score_other(self, ctx, user: discord.User, score: int):
        player = Player.get_player_from_user(user)
        self.data.score(player, score)
        self.save()
        await self.send_data_str(ctx, f"{player}'s score set to {score}")

    @base.command(**conf.Command.REMOVE_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def remove_other(self, ctx, user: discord.User):
        player = Player.get_player_from_user(user)
        self.data.remove_player(player)
        self.save()
        await self.send_data_str(ctx, f'{player} removed')

    @base.command(**conf.Command.SET_MESSAGE)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def set_message(self, ctx, *, msg: str):
        self.data.set_msg(msg)
        self.save()
        await self.send_data_str(ctx, 'Message Set')
