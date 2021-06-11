import logging

import discord
from discord.ext import commands

from bot.registration.cog_registration import CogRegistration
from bot.settings.cog_settings import CogSettings
from bot.tournament.cog_tournament import CogTournament
from bot.unranked.cog_unranked import CogUnranked
from conf import Conf
from utils.log import log
from utils.misc import export
from utils.rate_limited_execution import RateLimitedExecution

conf = Conf.TopLevel
"""Map class with setting for this cog to variable"""


class Bot(commands.Bot):
    def __init__(self, **args):
        super().__init__(**args)

        self.db = args['db']
        self.cog_settings = CogSettings(self.db)
        self.cog_tournament = CogTournament(self.db)
        self.cog_unranked = CogUnranked(self.db)
        self.cog_registration = CogRegistration(self.db)
        self.add_cog(self.cog_settings)
        self.add_cog(self.cog_tournament)
        self.add_cog(self.cog_unranked)
        self.add_cog(self.cog_registration)

        @self.check
        def check_channel(ctx):
            """
            Global check on all categories
            :param ctx: The context
            :return: True if should proceed or false to stop command execution
            """
            if isinstance(ctx.message.channel, discord.DMChannel):
                return ctx.command.name in conf.Permissions.ALLOWED_DM_COMMANDS
            else:
                return ctx.channel.name in conf.Permissions.ALLOWED_CHANNELS

        # TOP Level Commands (No Category)
        @self.command(**conf.Command.PING)
        async def ping(ctx):
            """
            Responds with pong if bot can talk here
            :param ctx: The Context
            """
            await ctx.send('pong')

        @self.command(**conf.Command.DM)
        async def dm(ctx):
            """
            Causes the bot to send a DM to the user
            :param ctx: The Context
            """
            await ctx.send('ok let me try one sec')
            await ctx.author.send("Here's the DM you requested.")

        @self.command(**conf.Command.VERSION)
        async def version(ctx):
            """
            Responds with the version of the bot
            :param ctx: The Context
            """
            await ctx.send(f'Version: {Conf.VERSION}')

        @self.command(**conf.Command.SAVE)
        @commands.has_any_role(*conf.Permissions.PRIV_ROLES)
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
                    role.name in conf.Permissions.PRIV_ROLES for role in
                    ctx.author.roles)

        @self.command(**conf.Command.EXPORT)
        @commands.check(is_dm_or_priv_role)
        async def export_cmd(ctx):
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

        @self.event
        async def on_member_join(member):
            await member.guild.system_channel.send(conf.WELCOME_MSG.substitute(
                mention=member.mention))

        @self.event
        async def on_member_remove(member):
            channel = self.get_channel(conf.INTERNAL_CHANNEL_ID)
            await channel.send(conf.MEMBER_LEAVE.substitute(name=f'{member}'))

    def get_tournament_as_html(self):
        return self.cog_tournament.as_html()

    def export(self):
        export(Conf.EXPORT_FILE_NAME, self.db)
