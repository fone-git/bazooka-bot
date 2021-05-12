import logging
import os
from threading import Thread

import discord
import flask
import yaml
from discord.ext import commands
from waitress import serve

from conf import Conf
from log import log, setup_logging
from tournament import Tournament

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

try:
    from replit import db
except ModuleNotFoundError:
    db = {}  # For working locally (Assume empty db)


def get_user_info(user):
    return str(user), user.name


def save_tournament(data):
    data = yaml.dump(data, Dumper=Dumper)
    db[Conf.KEY.TOURNAMENT] = data


tournament = db.get(Conf.KEY.TOURNAMENT)
if tournament is None:
    tournament = Tournament()
else:
    tournament = yaml.load(tournament, Loader=Loader)

#######################################################################
""" 
    HTML Control Section
    Had to put them in the same file to resolve issues with getting 
    access to current tournament variable values
    
"""
app = flask.Flask('Board')


@app.route('/')
def home():
    return flask.render_template('board.html', content=tournament.as_html())


def run():
    serve(app, host="0.0.0.0", port=8080)


def display_start():
    Thread(target=run).start()


#######################################################################

def main():
    log('Main Started')

    bot = commands.Bot(command_prefix=Conf.COMMAND_PREFIX)

    @bot.command(**Conf.COMMAND.REGISTER)
    async def register(ctx):
        user_fq, user_display = get_user_info(ctx.author)
        id_ = tournament.register(user_fq, user_display)
        save_tournament(tournament)
        await ctx.send(f'{user_display} registered with id: {id_}')

    @bot.command(**Conf.COMMAND.DISPLAY)
    async def display(ctx, full=None):
        if full is not None:
            tournament.calc_all_rounds()
        await ctx.send(tournament)

    @bot.command(**Conf.COMMAND.RESET)
    async def reset(ctx, confirm=None):
        if confirm != 'yes':
            await ctx.send('Are you sure you want to reset tournament (May cause data loss)? '
                           '(reset with argument of "yes" to confirm.')
        else:
            global tournament
            tournament = Tournament()
            save_tournament(tournament)
            await ctx.send("Tournament reset")

    @bot.command(**Conf.COMMAND.UNREGISTER)
    async def unregister(ctx):
        user_fq, user_display = get_user_info(ctx.author)
        id_ = tournament.unregister(user_fq, user_display)
        save_tournament(tournament)
        await ctx.send(f'{user_display} unregistered. ID was {id_}')

    @bot.command(**Conf.COMMAND.REGISTER_OTHER)
    async def register_other(ctx, at_ref_for_other: discord.User):
        user_fq, user_display = get_user_info(at_ref_for_other)
        id_ = tournament.register(user_fq, user_display)
        save_tournament(tournament)
        await ctx.send(f'{user_display} registered with id: {id_}')

    @bot.command(**Conf.COMMAND.UNREGISTER_OTHER)
    async def unregister_other(ctx, at_ref_for_other: discord.User):
        user_fq, user_display = get_user_info(at_ref_for_other)
        id_ = tournament.unregister(user_fq, user_display)
        save_tournament(tournament)
        await ctx.send(f'{user_display} unregistered. ID was {id_}')

    @bot.command(**Conf.COMMAND.SHUFFLE)
    async def shuffle(ctx):
        tournament.shuffle()
        save_tournament(tournament)
        await ctx.send(f'Player order shuffled')

    @bot.command(**Conf.COMMAND.COUNT)
    async def count(ctx):
        await ctx.send(tournament.count_as_str())

    @bot.command(**Conf.COMMAND.STATUS)
    async def status(ctx):
        await ctx.send(tournament.status())

    @bot.command(**Conf.COMMAND.START)
    async def start(ctx, rounds_best_out_of):
        tournament.start([int(x) for x in rounds_best_out_of.split()])
        await ctx.send(f'Tournament Started')

    @bot.command(**Conf.COMMAND.REOPEN_REGISTRATION)
    async def reopen_registration(ctx):
        tournament.reopen_registration()
        await ctx.send(f'Registration has been reopened. All progress erased.')

    @bot.command(**Conf.COMMAND.WIN)
    async def win(ctx, user: discord.User, qty: int = 1):
        user_fq, user_display = get_user_info(user)
        response = tournament.win(user_fq, user_display, qty)
        save_tournament(tournament)
        await ctx.send(response)

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
