import discord
from discord.ext import commands

from bot.common.cog_common import CogCommon
from bot.common.player import Player
from bot.unranked.unranked import Unranked
from conf import Conf, DBKeys
from utils import db_cache

conf = Conf.Unranked
"""Map class with setting for this cog to variable"""


class CogUnranked(CogCommon, name='Unranked'):
    data: Unranked  # Specify type of attribute for linting

    def __init__(self, db: db_cache):
        super().__init__(db, conf=conf, db_key=DBKeys.UNRANKED,
                         data_def_constructor=Unranked)

    ##########################################################################
    # NORMAL COMMANDS
    @commands.command(**conf.Command.SCORE)
    async def score(self, ctx, score: int):
        player = Player.get_player_from_user(ctx.author)
        self.data.score(player, score)
        self.save()
        await self.send_ranking_msg(ctx)

    @commands.command(**conf.Command.DISPLAY)
    async def display(self, ctx):
        await self.send_ranking_msg(ctx)

    ##########################################################################
    # PRIVILEGED COMMANDS
    @commands.command(**conf.Command.RESET)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def reset(self, ctx, confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data = self.data_def_constructor()
        self.save()
        await ctx.send("Unranked Reset")

    @commands.command(**conf.Command.SCORE_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def score_other(self, ctx, user: discord.User, score: int):
        player = Player.get_player_from_user(user)
        self.data.score(player, score)
        self.save()
        await self.send_ranking_msg(ctx)

    @commands.command(**conf.Command.REMOVE_PLAYER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def remove_player(self, ctx, user: discord.User):
        player = Player.get_player_from_user(user)
        self.data.remove_player(player)
        self.save()
        await ctx.send(f'{player} removed')

    @commands.command(**conf.Command.SET_MESSAGE)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def set_message(self, ctx, *, msg: str):
        self.data.set_msg(msg)
        self.save()
        await self.send_ranking_msg(ctx)

    ##########################################################################
    # HELPER FUNCTIONS
    async def send_ranking_msg(self, ctx):
        await ctx.send(self.data)
