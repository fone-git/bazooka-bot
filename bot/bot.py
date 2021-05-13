from discord.ext import commands

from bot.cog_tournament import CogTournament
from conf import Conf


class Bot(commands.Bot):
    def __init__(self, **args):
        super().__init__(**args)
        self.add_cog(CogTournament())

        # TOP Level Commands (No Category)
        @self.command(**Conf.COMMAND.PING)
        async def ping(ctx):
            await ctx.send("pong")
