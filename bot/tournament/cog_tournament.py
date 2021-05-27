import logging
import traceback
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Group

from bot.tournament.player import Player
from bot.tournament.tournament import Tournament
from conf import Conf, DBKeys
from utils.log import log
from utils.misc import get_user_info

# Map class with setting for this cog to variable
conf = Conf.TOURNAMENT


class CogTournament(commands.Cog, name='Tournament'):
    def __init__(self, db: dict):
        self.db = db
        self.data = self.load()

        self.last_save_time = datetime.now()
        self.save_timer = None
        # self.fix_recreate_players() # Use to update objects to match new code

    # GLOBALLY APPLIED FUNCTIONS
    def cog_check(self, ctx):
        return ctx.channel.name in conf.PERMISSIONS.ALLOWED_CHANNELS

    ##########################################################################
    # NORMAL COMMANDS
    @commands.command(**conf.COMMAND.REGISTER)
    async def register(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        disp_id = self.data.register(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} registered with id: {disp_id}')

    @commands.command(**conf.COMMAND.UNREGISTER)
    async def unregister(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        disp_id = self.data.unregister(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} unregistered. ID was {disp_id}')

    @commands.command(**conf.COMMAND.DISPLAY)
    async def display(self, ctx, full=None):
        if full is not None:
            if self.data.calc_all_rounds():
                self.save()
        await ctx.send(embed=self.data.as_embed())

    @commands.command(**conf.COMMAND.COUNT)
    async def count(self, ctx):
        await ctx.send(self.data.count_as_str())

    @commands.command(**conf.COMMAND.STATUS)
    async def status(self, ctx):
        # TODO Add if data is pending save to output and make restricted
        await ctx.send(self.data.status())

    @commands.command(**conf.COMMAND.WIN)
    async def win(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        response = self.data.win(user_id, user_display, 1)
        self.save()
        await ctx.send(response)

    ##########################################################################
    # PRIVILEGED COMMANDS
    @commands.command(**conf.COMMAND.WIN_OTHER)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def win_other(self, ctx, user: discord.User, qty: int = 1):
        user_id, user_display = get_user_info(user)
        response = self.data.win(user_id, user_display, qty)
        self.save()
        await ctx.send(response)

    @commands.command(**conf.COMMAND.RESET)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def reset(self, ctx, confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data = Tournament()
        self.save()
        await ctx.send("Tournament reset")

    @commands.command(**conf.COMMAND.REGISTER_OTHER)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def register_other(self, ctx, at_ref_for_other: discord.User):
        user_id, user_display = get_user_info(at_ref_for_other)
        disp_id = self.data.register(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} registered with id: {disp_id}')

    @commands.command(**conf.COMMAND.UNREGISTER_OTHER)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def unregister_other(self, ctx, at_ref_for_other: discord.User):
        user_id, user_display = get_user_info(at_ref_for_other)
        disp_id = self.data.unregister(user_id, user_display)
        self.save()
        await ctx.send(f'{user_display} unregistered. ID was {disp_id}')

    @commands.command(**conf.COMMAND.START)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def start(self, ctx, *, rounds_best_out_of: str):
        try:
            self.data.start([int(x) for x in rounds_best_out_of.split()])
            self.save()
            await ctx.send(f'Tournament Started')
        except Exception:
            traceback.print_exc()
            raise

    @commands.command(**conf.COMMAND.REOPEN_REGISTRATION)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def reopen_registration(self, ctx, confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data.reopen_registration()
        self.save()
        await ctx.send(f'Registration has been reopened. All progress erased.')

    @commands.command(**conf.COMMAND.SHUFFLE)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def shuffle(self, ctx):
        self.data.shuffle()
        self.save()
        await ctx.send(f'Player order shuffled')

    @commands.command(**conf.COMMAND.OVERRIDE)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def shuffle(self, ctx):
        self.data.shuffle()
        self.save()
        await ctx.send(f'Player order shuffled')

    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    @commands.group(pass_context=False, invoke_without_command=True)
    async def first(self, ctx):
        await ctx.send("Ping 1")
        command = self.first
        if isinstance(command, Group):  # check if it has subcommands
            embed = discord.Embed(title=f"{str(command).upper()} Help!",
                                  description='test', color=0xf8f8ff)
            resp = ""  # make an empty string to add the subcommands on
            for subcommand in command.walk_commands():  # iterate through
                # all of the command's parents/subcommands

                if subcommand.parents[0] == command:
                    # check if the latest parent of the
                    # subcommand is the command itself
                    resp += "**•  {0.name}**\n".format(
                        subcommand)  # then add it in the string if it is.
                else:  # the else statement is optional.
                    continue

            embed.add_field(name='Subcommands', value=resp, inline=False)
            embed.set_footer(text='<> - required | [] - optional')
            await ctx.send("test msg", embed=embed)

    @first.group(pass_context=False, invoke_without_command=True)
    async def second(self, ctx):
        await ctx.send("Ping 2")

    @first.group(pass_context=False, invoke_without_command=True)
    async def second2(self, ctx):
        await ctx.send("Ping 2")

    @second.command(pass_context=False)
    async def third(self, ctx):
        await ctx.send("Ping 3")

    @second.command(pass_context=False)
    async def third2(self, ctx):
        await ctx.send("Ping 32")

    @second.command(pass_context=False)
    async def four(self, ctx):
        await ctx.send("Ping 41")

    @second.command(pass_context=False)
    async def four2(self, ctx):
        await ctx.send("Ping 42")

    ##########################################################################
    # HELPER FUNCTIONS
    def save(self):
        log('[CogTournament] Call to save Tournament')
        self.db[DBKeys.TOURNAMENT, True] = self.data

    def load(self) -> Tournament:
        # noinspection PyArgumentList
        result = self.db.get(DBKeys.TOURNAMENT, should_yaml=True)
        if result is None:
            # Create new empty tournament
            result = Tournament()
        return result

    @staticmethod
    async def should_exec(ctx, confirm):
        if confirm:
            return True
        else:
            await ctx.send('Are you sure you want to execute this command?\n\n'
                           '```diff\n-WARNING: May cause data loss```\n\n'
                           'Resend command with argument of "yes" if you are '
                           'sure.')
            return False

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
