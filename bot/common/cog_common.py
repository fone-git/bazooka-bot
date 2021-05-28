from abc import abstractmethod

from discord.ext import commands

from utils import db_cache


class CogCommon(commands.Cog):
    def __init__(self, db: db_cache, *, conf):
        self.db = db
        self.conf = conf
        self.data = self.load()

    # GLOBALLY APPLIED FUNCTIONS
    def cog_check(self, ctx):
        return ctx.channel.name in self.conf.Permissions.ALLOWED_CHANNELS

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self):
        pass

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
