import logging
import os

from discord.ext import commands

from board_display import display_start
from conf import Conf
from log import log, setup_logging
from tournament import Tournament

try:
    from replit import db
except ModuleNotFoundError:
    db = {}  # For working locally (Assume empty db)


def get_user_info(user):
    return str(user), user.name


def save_tournament(data):
    db[Conf.KEY.TOURNAMENT] = data


def main():
    log('Main Started')

    tournament = db.get(Conf.KEY.TOURNAMENT)
    if tournament is None:
        tournament = Tournament()

    bot = commands.Bot(command_prefix=Conf.COMMAND_PREFIX)

    @bot.command(**Conf.COMMAND.REGISTER)
    async def register(ctx):
        user_fq, user_display = get_user_info(ctx.author)
        id_ = tournament.register(user_fq, user_display)
        await ctx.send(f'{user_display} registered with id: {id_}')
        save_tournament(tournament)

    @bot.command(**Conf.COMMAND.DISPLAY)
    async def display(ctx):
        await ctx.send(tournament)

    @bot.command(**Conf.COMMAND.RESET)
    async def reset(ctx, confirm=None):
        if confirm != 'yes':
            await ctx.send('Are you sure you want to reset tournament (May cause data loss)? '
                           '(reset with argument of "yes" to confirm.')
        else:
            nonlocal tournament
            tournament = Tournament()
            save_tournament(tournament)
            await ctx.send("Tournament reset")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            log(error, logging.DEBUG)
            await ctx.send('Command Not Found (Maybe you have a typo)')
        elif isinstance(error, commands.errors.UserInputError):
            log(error, logging.INFO)
            await ctx.send(error)
        else:
            log(error, logging.WARNING)
            await ctx.send('Command Failed')

    @bot.event
    async def on_ready():
        log(f'Successfully logged in as {bot.user}')

    display_start()
    bot.run(os.getenv(Conf.ENV.TOKEN))


if __name__ == '__main__':
    setup_logging()
    main()
