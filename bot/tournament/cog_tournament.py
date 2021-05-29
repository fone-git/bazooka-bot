import logging
import traceback

import discord
from discord.ext import commands

from bot.common.cog_common import CogCommon
from bot.common.player import Player
from bot.tournament.tournament import Tournament
from conf import Conf, DBKeys
from utils import db_cache
from utils.log import log
from utils.misc import get_user_info

conf = Conf.Tournament
"""Map class with setting for this cog to variable"""


class CogTournament(CogCommon, name='Tournament'):
    def __init__(self, db: db_cache):
        super().__init__(db, conf=conf, db_key=DBKeys.TOURNAMENT,
                         data_def_constructor=self.create_new_tournament)

        # self.fix_recreate_players() # Use to update objects to match new code

    ##########################################################################
    # NORMAL COMMANDS
    @commands.command(**conf.Command.REGISTER)
    async def register(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        disp_id = self.data.register(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} registered with id: {disp_id}')

    @commands.command(**conf.Command.UNREGISTER)
    async def unregister(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        disp_id = self.data.unregister(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} unregistered. ID was {disp_id}')

    @commands.command(**conf.Command.DISPLAY)
    async def display(self, ctx, full=None):
        if full is not None:
            if self.data.calc_all_rounds():
                self.save()
        await ctx.send(embed=self.data.as_embed())

    @commands.command(**conf.Command.COUNT)
    async def count(self, ctx):
        await ctx.send(self.data.count_as_str())

    @commands.command(**conf.Command.STATUS)
    async def status(self, ctx):
        await ctx.send(self.data.status())

    @commands.command(**conf.Command.WIN)
    async def win(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        response = self.data.win(user_id, user_display, 1)
        self.save()
        await ctx.send(response)

    ##########################################################################
    # PRIVILEGED COMMANDS
    @commands.command(**conf.Command.WIN_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def win_other(self, ctx, user: discord.User, qty: int = 1):
        user_id, user_display = get_user_info(user)
        response = self.data.win(user_id, user_display, qty)
        self.save()
        await ctx.send(response)

    @commands.command(**conf.Command.RESET)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def reset(self, ctx, confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data = self.data_def_constructor()
        self.save()
        await ctx.send("Tournament reset")

    @commands.command(**conf.Command.REGISTER_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def register_other(self, ctx, at_ref_for_other: discord.User):
        user_id, user_display = get_user_info(at_ref_for_other)
        disp_id = self.data.register(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} registered with id: {disp_id}')

    @commands.command(**conf.Command.UNREGISTER_OTHER)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def unregister_other(self, ctx, at_ref_for_other: discord.User):
        user_id, user_display = get_user_info(at_ref_for_other)
        disp_id = self.data.unregister(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} unregistered. ID was {disp_id}')

    @commands.command(**conf.Command.START)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def start(self, ctx, *, rounds_best_out_of: str):
        try:
            self.data.start([int(x) for x in rounds_best_out_of.split()])
            self.save()
            await ctx.send(f'Tournament Started')
        except Exception:
            traceback.print_exc()
            raise

    @commands.command(**conf.Command.REOPEN_REGISTRATION)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def reopen_registration(self, ctx, confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data.reopen_registration()
        self.save()
        await ctx.send(f'Registration has been reopened. All progress erased.')

    @commands.command(**conf.Command.SHUFFLE)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def shuffle(self, ctx):
        self.data.shuffle()
        self.save()
        await ctx.send(f'Player order shuffled')

    @commands.group(invoke_without_command=True, **conf.Command.Override.BASE)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def override(self, ctx):
        await ctx.send(f'Unrecognized subcommand')

    @override.command(**conf.Command.Override.SET)
    @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
    async def set(self, ctx, who: discord.User, game_id: int, player_pos: int):
        user_id, user_display = get_user_info(who)
        round_display = self.data.override_set(user_id, user_display, game_id,
                                               player_pos)
        self.save()
        await ctx.send(
            f'Scores reset for game: {game_id} and match up is now:\n'
            f'{round_display}')

    ##########################################################################
    # HELPER FUNCTIONS
    def as_html(self):
        return self.data.as_html()

    def fix_recreate_players(self):
        """
        Utility method used when updated happen to player fields during a
        active tournament to apply the change.
        NOTE: Only works during registration.
        """
        if not self.data.is_reg_open:
            log('[CogTournament]  Registration closed. Fix not applied to '
                'recreate players.',
                logging.ERROR)
            return
        replacement = []
        for x in self.data.players:
            replacement.append(Player(x.id, x.display, x.disp_id))
        self.data.players = replacement
        self.data.invalidate_computed_values()

    def create_new_tournament(self):
        result = Tournament()
        result.on_state_change = self.save
        return result
