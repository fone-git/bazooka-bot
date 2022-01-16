import typing
from typing import Union

import discord
from discord.ext import commands

from bot.common.cog_common import CogCommon
from bot.common.player import Player
from bot.registration.registration import Registration
from conf import Conf, DBKeys
from utils import db_cache

conf = Conf.Registration
"""Map class with setting for this cog to variable"""


class CogRegistration(CogCommon, name='Ideas'):
    data: Registration  # Specify type of attribute for linting

    def __init__(self, db: db_cache):
        super().__init__(db, conf=conf, db_key=DBKeys.REGISTRATION,
                         data_def_constructor=Registration)

    ##########################################################################
    # BASE GROUP
    @commands.group(**conf.BASE_GROUP)
    async def base(self, ctx):
        await super().base(ctx)

    ##########################################################################
    # NORMAL COMMANDS
    @base.command(**conf.Command.DISPLAY)
    async def display(self, ctx):
        await self.send_data_str(ctx)

    @base.command(**conf.Command.REGISTER)
    async def register(self, ctx, idea_number: Union[int, str] = None):
        await self.register_other(ctx, ctx.author, idea_number)

    @base.command(**conf.Command.UNREGISTER)
    async def unregister(self, ctx, idea_number: Union[int, str] = None):
        await self.unregister_other(ctx, ctx.author, idea_number)

    @base.command(**conf.Command.CAT_NEW)
    async def category_new(self, ctx, number: typing.Optional[int] = -1, *,
                           name: str):
        self.data.category_new(name, number)
        self.save()
        await self.send_data_str(ctx, f'New idea "{name}" added.')

    ##########################################################################
    # PRIVILEGED COMMANDS
    @base.command(**conf.Command.RESET)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def reset(self, ctx, are_mutually_exclusive_events: bool,
                    confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data = self.data_def_constructor(are_mutually_exclusive_events)
        self.save()
        await ctx.send(
            f"Ideas Reset - " +
            ('Single vote'
             if are_mutually_exclusive_events else
             'Multiple votes') +
            ' allowed')

    @base.command(**conf.Command.CAT_REMOVE)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def category_remove(self, ctx, number: int):
        name = self.data.category_remove(number)
        self.save()
        await self.send_data_str(ctx, f'Idea "{name}" removed.')

    @base.command(**conf.Command.CAT_RENAME)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def category_rename(self, ctx, number: int, *, new_name: str):
        self.data.category_rename(number, new_name)
        self.save()
        await self.send_data_str(ctx, f'Idea renamed.')

    @base.command(**conf.Command.REGISTER_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def register_other(self, ctx, user: discord.User,
                             cat_number: Union[int, str] = None):
        player = Player.get_player_from_user(user)
        self.data.register(player, cat_number)
        self.save()
        await self.send_data_str(ctx,
                                 f"{player} voted for idea "
                                 f"{cat_number}")

    @base.command(**conf.Command.UNREGISTER_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def unregister_other(self, ctx, user: discord.User,
                               cat_number: Union[int, str] = None):
        player = Player.get_player_from_user(user)
        self.data.unregister(player, cat_number)
        self.save()
        await self.send_data_str(ctx,
                                 f'{player}\'s vote removed from idea '
                                 f'{cat_number}')

    @base.command(**conf.Command.SET_MESSAGE)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def set_message(self, ctx, *, msg: str = None):
        self.data.set_msg(msg)
        self.save()
        await self.send_data_str(ctx, 'Message Set')
