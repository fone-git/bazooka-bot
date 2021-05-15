import traceback

import discord
import yaml
from discord.ext import commands

from bot.tournament.tournament import Tournament
from conf import Conf, DBKeys
from utils.misc import get_user_info

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# Map class with setting for this cog to variable
conf = Conf.TOURNAMENT


class CogTournament(commands.Cog, name='Tournament'):
    def __init__(self, db: dict):
        self.db = db
        self.data = self.load()

    # GLOBALLY APPLIED FUNCTIONS
    def cog_check(self, ctx):
        return ctx.channel.name in conf.PERMISSIONS.ALLOWED_CHANNELS

    ##########################################################################
    # NORMAL COMMANDS
    @commands.command(**conf.COMMAND.REGISTER)
    async def register(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        disp_id = self.data.register(user_id, user_display)
        self.invalidate_data()
        await ctx.send(f'{user_display} registered with id: {disp_id}')

    @commands.command(**conf.COMMAND.UNREGISTER)
    async def unregister(self, ctx):
        user_id, user_display = get_user_info(ctx.author)
        disp_id = self.data.unregister(user_id, user_display)
        self.invalidate_data()
        await ctx.send(f'{user_display} unregistered. ID was {disp_id}')

    @commands.command(**conf.COMMAND.DISPLAY)
    async def display(self, ctx, full=None):
        # TODO Change to any true
        if full is not None:
            self.data.calc_all_rounds()
        await ctx.send(self.data)

    @commands.command(**conf.COMMAND.COUNT)
    async def count(self, ctx):
        await ctx.send(self.data.count_as_str())

    @commands.command(**conf.COMMAND.STATUS)
    async def status(self, ctx):
        # TODO Add if data is pending save to output and make restricted
        await ctx.send(self.data.status())

    ##########################################################################
    # PRIVILEGED COMMANDS
    @commands.command(**conf.COMMAND.WIN)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def win(self, ctx, user: discord.User, qty: int = 1):
        user_id, user_display = get_user_info(user)
        response = self.data.win(user_id, user_display, qty)
        self.invalidate_data()
        await ctx.send(response)

    @commands.command(**conf.COMMAND.RESET)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def reset(self, ctx, confirm: bool = False):
        if not await self.should_exec(ctx, confirm):
            return

        self.data = Tournament()
        self.invalidate_data()
        await ctx.send("Tournament reset")

    @commands.command(**conf.COMMAND.REGISTER_OTHER)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def register_other(self, ctx, at_ref_for_other: discord.User):
        user_id, user_display = get_user_info(at_ref_for_other)
        disp_id = self.data.register(user_id, user_display)
        self.invalidate_data()
        await ctx.send(f'{user_display} registered with id: {disp_id}')

    @commands.command(**conf.COMMAND.UNREGISTER_OTHER)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def unregister_other(self, ctx, at_ref_for_other: discord.User):
        user_id, user_display = get_user_info(at_ref_for_other)
        disp_id = self.data.unregister(user_id, user_display)
        self.invalidate_data()
        await ctx.send(f'{user_display} unregistered. ID was {disp_id}')

    @commands.command(**conf.COMMAND.START)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def start(self, ctx, *, rounds_best_out_of: str):
        try:
            self.data.start([int(x) for x in rounds_best_out_of.split()])
            self.invalidate_data()
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
        self.invalidate_data()
        await ctx.send(f'Registration has been reopened. All progress erased.')

    @commands.command(**conf.COMMAND.SHUFFLE)
    @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
    async def shuffle(self, ctx):
        self.data.shuffle()
        self.invalidate_data()
        await ctx.send(f'Player order shuffled')

    ##########################################################################
    # HELPER FUNCTIONS
    def invalidate_data(self):
        # TODO: Add time delay to only save at most using once per period of time
        # TODO Add command to force save now to allow for shutdown
        self.save()

    def load(self) -> Tournament:
        db_data = self.db.get(DBKeys.TOURNAMENT)
        if db_data is None:
            # Create new empty tournament
            result = Tournament()
        else:
            result = yaml.load(db_data, Loader=Loader)
        return result

    def save(self):
        data = yaml.dump(self.data, Dumper=Dumper)
        self.db[DBKeys.TOURNAMENT] = data

    @staticmethod
    async def should_exec(ctx, confirm):
        if confirm:
            return True
        else:
            await ctx.send('Are you sure you want to execute this command?\n\n'
                           '```diff\n-WARNING: May cause data loss```\n\n'
                           'Resend command with argument of "yes" if you are sure.')
            return False

    def as_html(self):
        return self.data.as_html()

    def export(self):
        with open(Conf.EXPORT_FILE_NAME, 'w') as f:
            f.write(yaml.dump(self.data, Dumper=Dumper))
