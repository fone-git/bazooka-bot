import logging

import discord
import yaml
from discord.ext import commands

from bot.tournament.cog_tournament import CogTournament
from conf import Conf
from utils.log import log
from utils.rate_limited_execution import RateLimitedExecution

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# Map class with setting for this cog to variable
conf = Conf.TopLevel


class Bot(commands.Bot):
    # TODO investigate responding to at mention of the bot
    def __init__(self, **args):
        super().__init__(**args)

        if args.get('db') is not None:
            db = args['db']
        else:
            log('db not specified using empty dict', logging.WARNING)
            db = {}
        self.db = db
        self.cog_tournament = CogTournament(db)
        self.add_cog(self.cog_tournament)

        @self.check
        def check_channel(ctx):
            """
            Global check on all categories
            :param ctx: The context
            :return: True if should proceed or false to stop command execution
            """
            if isinstance(ctx.message.channel, discord.DMChannel):
                return ctx.command.name in conf.PERMISSIONS.ALLOWED_DM_COMMANDS
            else:
                return ctx.channel.name in conf.PERMISSIONS.ALLOWED_CHANNELS

        # TOP Level Commands (No Category)
        @self.command(**conf.COMMAND.PING)
        async def ping(ctx):
            """
            Responds with pong if bot can talk here
            :param ctx: The Context
            """
            await ctx.send('pong')

        @self.command(**conf.COMMAND.DM)
        async def dm(ctx):
            """
            Causes the bot to send a DM to the user
            :param ctx: The Context
            """
            await ctx.send('ok let me try one sec')
            await ctx.author.send("Here's the DM you requested.")

        @self.command(**conf.COMMAND.VERSION)
        async def version(ctx):
            """
            Responds with the version of the bot
            :param ctx: The Context
            """
            await ctx.send(f'Version: {Conf.VERSION}')

        @self.command(**conf.COMMAND.SAVE)
        @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
        async def save(ctx):
            """
            Requests that the bot saves to secondary storage immediately
            :param ctx: The Context
            """
            self.cog_tournament.save()
            await ctx.author.send("Saved")

        def is_dm_or_priv_role(ctx):
            if isinstance(ctx.message.channel, discord.DMChannel):
                return True
            else:
                return any(
                    role.name in conf.PERMISSIONS.PRIV_ROLES for role in
                    ctx.author.roles)

        @self.command(**conf.COMMAND.EXPORT)
        @commands.check(is_dm_or_priv_role)
        async def export(ctx):
            """
            Requests that the bot saves to a file
            :param ctx: The Context
            """
            RateLimitedExecution.get_instance().register(Conf.EXPORT_DELAY,
                                                         self.export)
            await ctx.author.send("Export Request Acknowledged")

        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.errors.CommandNotFound):
                log(error, logging.DEBUG)
                # No need for noisy fail message right now
                # await ctx.send('Command Not Found (Maybe you have a typo)')
            elif isinstance(error, commands.errors.UserInputError):
                log(error, logging.INFO)
                await ctx.send(error)
            elif isinstance(error, commands.errors.MissingAnyRole):
                log(error, logging.INFO)
                await ctx.send('Restricted Command')
            elif isinstance(error, commands.errors.CheckFailure):
                log(error,
                    logging.DEBUG)  # Mostly expected to be because of wrong
                # channel
            else:
                # Command failed for an unexpected reason. Usually this
                # shouldn't happen
                log(error, logging.WARNING)
                await ctx.send('Command Failed!!!')

        @self.event
        async def on_ready():
            log(f'Successfully logged in as {self.user}')

    def get_tournament_as_html(self):
        return self.cog_tournament.as_html()

    def export(self):
        exp_dict = {}
        for key in self.db.keys():
            exp_dict[key] = self.db[key]
        with open(Conf.EXPORT_FILE_NAME, 'w') as f:
            f.write(yaml.dump(exp_dict, Dumper=Dumper))
