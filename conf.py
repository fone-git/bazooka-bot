class Conf:
    class COMMAND:
        REGISTER = {
            'name': 'reg',
            'help': 'registers you for the tournament'}
        
        DISPLAY = {
            'name': 'display',
            'help': 'Shows current board state'}

    COMMAND_PREFIX = '!'

    class ENV:  # Environment variable names
        TOKEN = 'TOKEN'

    class KEY:  # Database key values
        TOURNAMENT = 'tournament'
