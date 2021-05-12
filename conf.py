class Conf:
    class COMMAND:
        REGISTER = {
            'name': 'reg',
            'help': 'Registers you for the tournament'}
        UNREGISTER = {
            'name': 'unreg',
            'help': 'Unregisters you for the tournament'}
        DISPLAY = {
            'name': 'display',
            'help': 'Shows current board state'}
        RESET = {
            'name': 'reset',
            'help': 'Starts a new tournament. WARNING: Old data is cleared'}
        REGISTER_OTHER = {
            'name': 'reg_other',
            'help': 'Registers someone else  for the tournament'}
        UNREGISTER_OTHER = {
            'name': 'unreg_other',
            'help': 'Unregisters someone else from the tournament'}

    COMMAND_PREFIX = '!'

    class ENV:  # Environment variable names
        TOKEN = 'TOKEN'

    class KEY:  # Database key values
        TOURNAMENT = 'tournament'
