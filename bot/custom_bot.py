import logging

from discord.ext import commands

from bot.tournament.cog_tournament import CogTournament
from conf import Conf
from utils.log import log

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
        self.cog_tournament = CogTournament(db)
        self.add_cog(self.cog_tournament)

        @self.check
        def check_channel(ctx):
            """
            Global check on all categories
            :param ctx: The context
            :return: True if should proceed or false to stop command execution
            """
            return ctx.channel.name in conf.PERMISSIONS.ALLOWED_CHANNELS

        # TOP Level Commands (No Category)
        @self.command(**conf.COMMAND.PING)
        async def ping(ctx):
            """
            Responds with pong if bot can talk here
            :param ctx: The Context
            """
            await ctx.send('pong')

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

        @self.command(**conf.COMMAND.EXPORT)
        @commands.has_any_role(*conf.PERMISSIONS.PRIV_ROLES)
        async def export(ctx):
            """
            Requests that the bot saves to a file
            :param ctx: The Context
            """
            self.cog_tournament.export()
            await ctx.author.send("Exported")

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
        with open(Conf.EXPORT_FILE_NAME, 'w') as f:
            f.write(yaml.dump(self.data, Dumper=Dumper))
