import logging


# TODO Add option to chose to use qualifying round

class MasterPermissions:
    class PRIV:
        TOURNAMENT = {'@officer', '@leader'}
        TOP = TOURNAMENT

    class Channels:
        TOURNAMENT = {'tournament', 'bot-commands'}
        TOP_ONLY = {'general', 'bazooka-supreme-eng'}
        TOP = TOP_ONLY.union(TOURNAMENT)


class DBKeys:  # Database key values
    TOURNAMENT = 'tournament'


class Conf:
    BOT_DESCRIPTION = "Bazooka Alliance BOT"
    VERSION = '1.9.3'
    LOG_LEVEL = logging.INFO
    COMMAND_PREFIX = 'bb'
    SAVE_CACHE_DELAY = 30  # Minimum number of seconds between saves
    EXPORT_FILE_NAME = 'export.yaml'
    EXPORT_DELAY = 15
    EMBED_COLOR = 0x373977

    class ENV:  # Environment variable names
        TOKEN = 'TOKEN'

    class TopLevel:
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

    class TOURNAMENT:
        # Number of seconds before automatically calculating all bracket
        AUTO_CALC_BRACKET_DELAY = 10

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
                'name': 'display',
                'help': 'Shows current board state. Add "full" argument to '
                        'force full board generation'}
            RESET = {
                'name': 'reset',
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
                    'hidden': True}
                SET = {
                    'name': 'set',
                    'help': 'Sets the specified player to play in the '
                            'specified position scores for the target game '
                            'are cleared.',
                    'hidden': True}
