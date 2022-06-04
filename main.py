import os
from threading import Thread

import discord
import flask
from discord.ext import commands
from opylib.log import log, setup_log
from waitress import serve

from bot.custom_bot import Bot
from conf import Conf
from utils.db_cache import DBCache
from utils.repl_support import get_db

#######################################################################
"""
Global Variables
"""

bot: Bot

##############################################################################
""" 
    HTML Control Section
    Had to put them in the same file to resolve issues with getting 
    access to current tournament variable values
    
"""
web_interface = flask.Flask('Board')


@web_interface.route('/')
def home():
    return flask.render_template(
        'board.html', content=bot.get_tournament_as_html())


def run():
    serve(web_interface, host="0.0.0.0", port=8080)


def display_start():
    Thread(target=run).start()


##############################################################################


def main():
    global bot
    setup_log(Conf.LOG_LEVEL)
    log('Main Started')

    intents = discord.Intents.default()
    # intents.members = True #TODO: Re-enable member event features

    bot = Bot(db=DBCache(get_db()),
              command_prefix=commands.when_mentioned_or(Conf.COMMAND_PREFIX),
              description=Conf.BOT_DESCRIPTION, intents=intents)

    display_start()
    bot.run(os.getenv(Conf.ENV.TOKEN))


if __name__ == '__main__':
    main()
