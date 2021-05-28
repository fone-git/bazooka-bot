from discord.ext import commands

from conf import Conf

# Map class with setting for this cog to variable
conf = Conf.Unranked


class CogUnranked(commands.Cog, name='Unranked'):
    def __init__(self, db: dict):
        self.db = db
        self.data = self.load()

    # GLOBALLY APPLIED FUNCTIONS
    def cog_check(self, ctx):
        return ctx.channel.name in conf.Permissions.ALLOWED_CHANNELS

    def load(self):
        pass
