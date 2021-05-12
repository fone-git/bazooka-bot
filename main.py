import logging
import os

from discord.ext import commands

from board_display import display_start
from log import log, setup_logging

try:
    from replit import db
except ModuleNotFoundError:
    db = {}  # For working locally (Assume empty db)


def main():
    log('Main Started')

    bot = commands.Bot(command_prefix='!')

    @bot.command(name='reg', help='registers you for the tournament')
    async def register(ctx):
        await ctx.send(f'{ctx.author.name} registered')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send('Command Not Found (Maybe you have a typo)')
        else:
            await ctx.send('Command Failed')
        log(error, logging.WARNING)

    @bot.event
    async def on_ready():
        log(f'Logged in as {bot.user}')

    display_start()
    bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    setup_logging()
    main()
