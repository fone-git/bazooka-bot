import logging
from datetime import datetime

import discord
from discord.ext import commands
from opylib.log import log
from opylib.rate_limited_execution import RateLimitedExecution

from bot.registration.cog_registration import CogRegistration
from bot.settings.cog_settings import CogSettings
from bot.tournament.cog_tournament import CogTournament
from bot.unranked.cog_unranked import CogUnranked
from conf import Conf
from utils.connect_manager import ConnectManager
from utils.misc import debug_dump, export

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
            :return: True if execution should proceed or
                False to stop command execution
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
            self.db.purge()
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

        @self.command(**conf.Command.DEBUG_DUMP)
        @commands.check(is_dm_or_priv_role)
        async def debug_dump_cmd(ctx):
            """
            Requests that the bot saves to a file for debugging
            :param ctx: The Context
            """
            RateLimitedExecution.get_instance().register(Conf.DEBUG_DUMP_DELAY,
                                                         self.debug_dump)
            await ctx.author.send("Debug Dump Request Acknowledged")

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
            status = ConnectManager.status(self.db, add_discord_highlights=True)
            conn_status = (
                f'Successfully logged in as {self.user}\n'
                f'{status}')
            log(conn_status)
            if len(conn_status) > Conf.MAX_DISCORD_MSG_LEN:
                log(f'CONNECTION MESSAGE EXCEEDS LIMIT: {len(conn_status)}. '
                    f'Truncated')
                conn_status = conn_status[:Conf.MAX_DISCORD_MSG_LEN]
            ConnectManager.reset_fail_count(self.db)
            ConnectManager.set_last_conn_success(datetime.now(), self.db)
            ConnectManager.start_heartbeat(self.db)
            channel = self.get_channel(conf.DEBUG_CHANNEL_ID)
            if channel is not None:
                await channel.send(conn_status)
            else:
                log(f'Unable fo find channel with ID: {conf.DEBUG_CHANNEL_ID}')
            self.db.purge()  # Ensure logon information is saved

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

    def debug_dump(self):
        debug_dump(Conf.DEBUG_DUMP_FOLDER, self.db)
