import logging
from abc import abstractmethod

from discord.ext import commands

from utils import db_cache
from utils.log import log


class CogCommon(commands.Cog):
    def __init__(self, db: db_cache, *, conf, db_key=None,
                 data_def_constructor=None):
        self.data_def_constructor = data_def_constructor
        self.db_key = db_key
        self.db = db
        self.conf = conf
        self.data = self.load()

    # GLOBALLY APPLIED FUNCTIONS
    def cog_check(self, ctx):
        return ctx.channel.name in self.conf.Permissions.ALLOWED_CHANNELS

    ##########################################################################
    # BASE GROUP
    @abstractmethod
    async def base(self, ctx):
        await ctx.send("I'm sorry I didn't recognize that command")

    ##########################################################################
    # HELPER FUNCTIONS
    def save(self):
        if self.db_key is not None:
            log(f'[{self.__class__.__name__}] Call to save',
                logging.DEBUG)
            self.db[self.db_key, True] = self.data

    def load(self):
        if self.db_key is not None and self.data_def_constructor is not None:
            result = self.db.get(self.db_key, should_yaml=True)
            if result is None:
                # Create new empty instance of data
                result = self.data_def_constructor()
            return result
        else:
            return None

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

    async def send_data_str(self, ctx, msg_prefix: str = None):
        msg = '' if msg_prefix is None else f'{msg_prefix}\n\n'
        msg += str(self.data)
        await ctx.send(msg)
