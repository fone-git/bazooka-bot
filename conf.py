import logging
from string import Template


# TODO Add option to chose to use qualifying round instead of alternating byes

class MasterPermissions:
    class PRIV:
        TOURNAMENT = {'@officer', '@leader'}
        SETTINGS = TOURNAMENT  # Set to equal for now nothing more needed
        UNRANKED = TOURNAMENT  # Set to equal for now nothing more needed
        REGISTRATION = TOURNAMENT  # Set to equal for now nothing more needed
        TOP = TOURNAMENT

    class Channels:
        TOURNAMENT = {'tournament'}
        UNRANKED = {'unranked-challenge'}
        REGISTRATION = {'bazooka-supreme-eng'}
        TOP_ONLY = {'general', 'bazooka-supreme-eng'}
        TOP = TOP_ONLY.union(TOURNAMENT).union(UNRANKED)
        SETTINGS = TOP


class DBKeys:  # Database key values
    TOURNAMENT = 'tournament'
    UNRANKED = 'unranked'
    REGISTRATION = 'registration'


class Conf:
    BOT_DESCRIPTION = "Bazooka Alliance BOT"
    VERSION = '1.14'
    LOG_LEVEL = logging.INFO
    COMMAND_PREFIX = 'bb'
    SAVE_CACHE_DELAY = 30  # Minimum number of seconds between saves
    EXPORT_FILE_NAME = 'export.yaml'
    EXPORT_DELAY = 15
    URL = 'https://bazooka-bot.one23.repl.co/'
    EMBED_COLOR = 0x373977

    class ENV:  # Environment variable names
        TOKEN = 'TOKEN'

    class TopLevel:
        INTERNAL_CHANNEL_ID = 613723324018720787
        WELCOME_MSG = Template(
            "Welcome ${mention}. Nice to have you here. Make yourself at "
            "home. If you are looking to organize a race tie check out our "
            "<#744875911119110245>. If you are looking to join one of our "
            "alliances please post a screen shot of your previous season "
            "achievements in <#760521977072713758>. Otherwise you're welcome "
            "to just chill or Gents are also welcome to check out our "
            "<#757542001708105739>.")
        MEMBER_LEAVE = Template(
            "Hey, just letting you know I noticed ${name} left the server...")

        class Permissions:
            ALLOWED_DM_COMMANDS = {  # Hard coded to allow for debugging
                'export',
                'version',
                'ping',
            }
            ALLOWED_CHANNELS = MasterPermissions.Channels.TOP
            PRIV_ROLES = MasterPermissions.PRIV.TOP

        class Command:
            DM = {
                'name': 'dm',
                'help': 'Sends a DM to the user'}
            PING = {
                'name': 'ping',
                'help': 'Tests if the bot is alive. If alive bot responds '
                        'pong'}
            VERSION = {
                'name': 'version',
                'hidden': True}
            SAVE = {
                'name': 'save',
                'hidden': True}
            EXPORT = {
                'name': 'export',
                'hidden': True}

    class Tournament:
        BASE_GROUP = {'name': 't',
                      'help': 'Grouping for Tournament Commands',
                      'invoke_without_command': True}

        class Permissions:
            PRIV_ROLES = MasterPermissions.PRIV.TOURNAMENT
            ALLOWED_CHANNELS = MasterPermissions.Channels.TOURNAMENT

        class Command:
            REGISTER = {
                'name': 'reg',
                'help': 'Registers you for the tournament'}
            UNREGISTER = {
                'name': 'unreg',
                'help': 'Unregisters you for the tournament'}
            DISPLAY = {
                'name': 'disp',
                'help': 'Shows all fixtures'}
            NEW = {
                'name': 'new',
                'help': 'Starts a new tournament. WARNING: Old data is '
                        'cleared'}
            REGISTER_OTHER = {
                'name': 'reg_other',
                'help': 'Registers someone else  for the tournament'}
            UNREGISTER_OTHER = {
                'name': 'unreg_other',
                'help': 'Unregisters someone else from the tournament'}
            SHUFFLE = {
                'name': 'shuffle',
                'help': 'Shuffles the user order. NB: Only works during '
                        'registration.'}
            COUNT = {
                'name': 'count',
                'help': 'Returns the number of registered players and rounds'}
            STATUS = {
                'name': 'status',
                'help': 'Returns the status of the system including the '
                        'present state of registration'}
            START = {
                'name': 'start',
                'help': 'Starts the tournament. Stops registration and '
                        'disables shuffle.\n'
                        'NB: Must supply numbers indicating the best out of '
                        'how many games for each round.\n'
                        'Numbers should be space separated EG "start 1 3 5" '
                        'means that there are 3 '
                        'rounds the first is best of 1 the second is best of '
                        '3 and so on...'}
            REOPEN_REGISTRATION = {
                'name': 'reopen',
                'help': 'Reopens registration but erases any current '
                        'progress (all wins erased).'}
            WIN = {
                'name': 'win',
                'help': 'Allows a player to self report a win'}

            WIN_OTHER = {
                'name': 'win_other',
                'help': 'Increases the specified players points by a qty or '
                        '1 if not specified'}

            class Override:
                BASE = {
                    'name': 'override',
                    'hidden': True,
                    'invoke_without_command': True}
                SET = {
                    'name': 'set',
                    'help': 'Sets the specified player to play in the '
                            'specified position scores for the target game '
                            'are cleared.',
                    'hidden': True}

    class Settings:
        class Permissions:
            PRIV_ROLES = MasterPermissions.PRIV.SETTINGS
            ALLOWED_CHANNELS = MasterPermissions.Channels.SETTINGS

    class Unranked:
        MAX_SCORE = 10
        BASE_GROUP = {'name': 'ur',
                      'help': 'Grouping for Unranked Commands',
                      'invoke_without_command': True}

        class Command:
            SCORE = {
                'name': 'score',
                'help': 'Registers your score (Overwrites if already exists)'}

            DISPLAY = {
                'name': 'disp',
                'help': 'Shows the player rankings'}

            RESET = {
                'name': 'reset',
                'help': 'Clears all data. Resets to a new unranked challenge.'}

            SCORE_OTHER = {
                'name': 'score_other',
                'help': 'Registers the score for another player (Overwrites '
                        'if already exists)'}

            REMOVE = {
                'name': 'rem',
                'help': 'Removes a player from the rankings'}

            REMOVE_OTHER = {
                'name': 'rem_other',
                'help': 'Removes specified player from the rankings'}

            SET_MESSAGE = {
                'name': 'msg',
                'help': 'Sets the message that is displayed along with the '
                        'rankings. Can be used to display what deck to use '
                        'or other special instructions'}

        class Permissions:
            PRIV_ROLES = MasterPermissions.PRIV.UNRANKED
            ALLOWED_CHANNELS = MasterPermissions.Channels.UNRANKED

    class Registration:
        BASE_GROUP = {'name': 'r',
                      'help': 'Grouping for Registration List Commands',
                      'invoke_without_command': True}

        class Command:
            # TODO Allow option to allow registration to only one category
            # TODO Add option to set default category
            # TODO Add option to set category commands to require priv
            # TODO Add option to restrict use of all
            REGISTER = {
                'name': 'reg',
                'help': 'Registers you for the category specified (If only '
                        'one exists specification is not required)'}

            REGISTER_OTHER = {
                'name': 'reg_other',
                'help': 'Registers another user see help for self '
                        'registration for details on parameter'}

            UNREGISTER = {
                'name': 'unreg',
                'help': 'Unregisters user from category passed or "all" if '
                        'passed as parameter'}

            UNREGISTER_OTHER = {
                'name': 'unreg_other',
                'help': 'Unregisters another user from category passed or '
                        '"all" if passed as parameter'}

            CAT_NEW = {
                'name': 'cat_new',
                'help': 'Creates a new category'}

            CAT_REMOVE = {
                'name': 'cat_rem',
                'help': 'Removes a category'}

            CAT_RENAME = {
                'name': 'cat_rn',
                'help': 'Changes the description of a category'}

            DISPLAY = {
                'name': 'disp',
                'help': 'Shows the registered users'}

            RESET = {
                'name': 'reset',
                'help': 'Clears all data.'}

            SET_MESSAGE = {
                'name': 'msg',
                'help': 'Sets a general message that is displayed at the top.'}

        class Permissions:
            PRIV_ROLES = MasterPermissions.PRIV.REGISTRATION
            ALLOWED_CHANNELS = MasterPermissions.Channels.REGISTRATION
