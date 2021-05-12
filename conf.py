class Conf:
    class PERMISSIONS:
        PRIV_ROLES = {'officer', 'leader'}
        ALLOWED_CHANNELS = {'tournament', 'bot-test-messages'}

    class COMMAND:
        REGISTER = {
            'name': 'reg',
            'help': 'Registers you for the tournament'}
        UNREGISTER = {
            'name': 'unreg',
            'help': 'Unregisters you for the tournament'}
        DISPLAY = {
            'name': 'display',
            'help': 'Shows current board state. Add "full" argument to force full board generation'}
        RESET = {
            'name': 'reset',
            'help': 'Starts a new tournament. WARNING: Old data is cleared'}
        REGISTER_OTHER = {
            'name': 'reg_other',
            'help': 'Registers someone else  for the tournament'}
        UNREGISTER_OTHER = {
            'name': 'unreg_other',
            'help': 'Unregisters someone else from the tournament'}
        SHUFFLE = {
            'name': 'shuffle',
            'help': 'Shuffles the user order. NB: Only works during registration.'}
        COUNT = {
            'name': 'count',
            'help': 'Returns the number of registered players and rounds'}
        STATUS = {
            'name': 'status',
            'help': 'Returns the status of the system including the present state of registration'}
        START = {
            'name': 'start',
            'help': 'Starts the tournament. Stops registration and disables shuffle. '
                    'NB: Must supply number indicating the best out of how many games '
                    'for each round. Numbers should be space separated and quoted to be '
                    'one argument. EG start "1 3 3 5".'}
        REOPEN_REGISTRATION = {
            'name': 'reopen_reg',
            'help': 'Reopens registration but erases any current progress (all wins erased).'}
        WIN = {
            'name': 'win',
            'help': 'Increases the specified players points by a qty or 1 if not specified'}

    COMMAND_PREFIX = 'bb'

    class ENV:  # Environment variable names
        TOKEN = 'TOKEN'

    class KEY:  # Database key values
        TOURNAMENT = 'tournament'
