import logging
from datetime import timedelta
from string import Template


# TODO Add option to chose to use qualifying round instead of alternating byes
# TODO: Use channel id's instead of names to make more resilient

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
        REGISTRATION = UNRANKED
        TOP_ONLY = {'general', 'bazooka-internal-chatroom-eng',
                    'de-bug-bot-channel'}
        TOP = TOP_ONLY.union(TOURNAMENT).union(UNRANKED)
        SETTINGS = TOP


class DBKeys:  # Database key values
    TOURNAMENT = 'tournament'
    UNRANKED = 'unranked'
    REGISTRATION = 'registration'
    CM_LAST_CONN_SUCCESS_DT = 'cm_last_conn_success_date_time'
    CM_LAST_CONN_FAIL_INFO = 'cm_last_conn_fail'


class Conf:
    BOT_DESCRIPTION = "Bazooka Alliance BOT"
    VERSION = '1.19.6'
    LOG_LEVEL = logging.INFO
    COMMAND_PREFIX = 'bb'
    SAVE_CACHE_DELAY = 15  # Minimum number of seconds between saves
    EXPORT_FILE_NAME = 'export.yaml'
    DEBUG_DUMP_FOLDER = 'debug_dump/'
    EXPORT_DELAY = 15
    DEBUG_DUMP_DELAY = 5
    URL = 'https://bazooka-bot.one23.repl.co/'
    EMBED_COLOR = 0x373977
    FAILED_CONNECT_INITIAL_DELAY = timedelta(minutes=15)

    class ENV:  # Environment variable names
        TOKEN = 'TOKEN'

    class TopLevel:
        INTERNAL_CHANNEL_ID = 613723324018720787
        DEBUG_CHANNEL_ID = 863277419972395029
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
            DEBUG_DUMP = {
                'name': 'debug_dump',
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

            ONE = {
                'name': '1',
                'help': 'Sets the score as 1'}
            TWO = {
                'name': '2',
                'help': 'Sets the score as 2'}
            THREE = {
                'name': '3',
                'help': 'Sets the score as 3'}
            FOUR = {
                'name': '4',
                'help': 'Sets the score as 4'}
            FIVE = {
                'name': '5',
                'help': 'Sets the score as 5'}
            SIX = {
                'name': '6',
                'help': 'Sets the score as 6'}
            SEVEN = {
                'name': '7',
                'help': 'Sets the score as 7'}
            EIGHT = {
                'name': '8',
                'help': 'Sets the score as 8'}
            NINE = {
                'name': '9',
                'help': 'Sets the score as 9'}
            TEN = {
                'name': '10',
                'help': 'Sets the score as 10'}

        class Permissions:
            PRIV_ROLES = MasterPermissions.PRIV.UNRANKED
            ALLOWED_CHANNELS = MasterPermissions.Channels.UNRANKED

    class Registration:
        BASE_GROUP = {'name': 'idea',
                      'help': 'Grouping for Unranked Ideas List Commands',
                      'invoke_without_command': True}

        class Command:
            # TODO Allow option to allow registration to only one category
            # TODO Add option to set default category
            # TODO Add option to set category commands to require priv
            # TODO Add option to restrict use of all
            REGISTER = {
                'name': 'vote',
                'help': 'Votes for the idea specified'}

            REGISTER_OTHER = {
                'name': 'vote_other',
                'help': 'Registers another player\'s vote see help for self '
                        'voting for details on parameter'}

            UNREGISTER = {
                'name': 'unvote',
                'help': 'Removes a players vote from idea passed or "all" if '
                        'passed as parameter'}

            UNREGISTER_OTHER = {
                'name': 'unvote_other',
                'help': 'Removes another player\'s vote from the idea passed '
                        'or "all" if passed as parameter'}

            CAT_NEW = {
                'name': 'new',
                'help': 'Creates a new idea'}

            CAT_REMOVE = {
                'name': 'rem',
                'help': 'Removes an idea'}

            CAT_RENAME = {
                'name': 'rename',
                'help': 'Changes the description of an idea'}

            DISPLAY = {
                'name': 'disp',
                'help': 'Shows the current ideas and votes'}

            RESET = {
                'name': 'reset',
                'help': 'Clears all data.'}

            SET_MESSAGE = {
                'name': 'msg',
                'help': 'Sets a general message that is displayed at the top.'}

            CLEAR_REGISTRATIONS = {
                'name': 'clear_votes',
                'help': 'Removes all current votes.'}

            SET_MUTUALLY_EXCLUSIVE = {
                'name': 'set_vote_type',
                'help': 'Allows changing of vote type (may fail if multiple '
                        'votes currently exist and trying to change to '
                        'single, would need to be brought into a valid state '
                        'possibly via a clear).'}

        class Permissions:
            PRIV_ROLES = MasterPermissions.PRIV.REGISTRATION
            ALLOWED_CHANNELS = MasterPermissions.Channels.REGISTRATION
