import os
from threading import Thread
from typing import Optional

import discord
import flask
from discord.ext import commands
from opylib.log import log, set_log_level, setup_log
from waitress import serve

from bot.custom_bot import Bot
from conf import Conf
from utils.connect_manager import ConnectManager
from utils.db_cache import DBCache
from utils.repl_support import get_db

#######################################################################
"""
Global Variables
"""

bot: Optional[Bot] = None
connect_manager: ConnectManager

##############################################################################
""" 
    HTML Control Section
    Had to put them in the same file to resolve issues with getting 
    access to current tournament variable values
    
"""
web_interface = flask.Flask('Board')


@web_interface.route('/')
def home():
    global bot
    tournament_info = 'Bot not created yet' if bot is None else \
        bot.get_tournament_as_html()

    return flask.render_template(
        'board.html', content=tournament_info,
        status=connect_manager.status_as_html())


def run():
    serve(web_interface, host="0.0.0.0", port=8080)


def display_start():
    Thread(target=run).start()


##############################################################################

def connect(db):
    global bot
    intents = discord.Intents.default()
    intents.members = True
    bot = Bot(
        db=db,
        command_prefix=commands.when_mentioned_or(Conf.COMMAND_PREFIX),
        description=Conf.BOT_DESCRIPTION,
        intents=intents)
    bot.run(os.getenv(Conf.ENV.TOKEN))


def main():
    global bot, connect_manager
    setup_log(None, only_std_out=True)
    set_log_level(Conf.LOG_LEVEL)
    log('Main Started')
    db = DBCache(get_db())
    display_start()
    connect_manager = ConnectManager(connect, db)
    connect_manager.do_try_connect()


if __name__ == '__main__':
    main()
