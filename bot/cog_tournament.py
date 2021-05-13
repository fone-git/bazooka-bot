from discord.ext import commands

from conf import Conf
from uitls.misc import get_user_info


class CogTournament(commands.Cog):

    @commands.command(**Conf.COMMAND.REGISTER)
    async def register(self, ctx):
        user_fq, user_display = get_user_info(ctx.author)
        await ctx.send(f'message received')
