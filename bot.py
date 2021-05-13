from discord.ext import commands

from conf import Conf


class Bot(commands.Bot):
    def __init__(self, **args):
        super().__init__(**args)

        # TOP Level Commands (No Category)
        @self.command(**Conf.COMMAND.PING)
        async def ping(ctx):
            await ctx.send("pong")
