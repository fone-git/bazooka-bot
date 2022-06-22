from bot.common.player_list import PlayerList


class Category(PlayerList):
    def __init__(self, number: int = 1, name: str = 'Default'):
        super().__init__()
        self.number: int = number
        self._name: str = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._invalidate_calculated()

    def get_str_rep(self, show_players=False):
        players = '' if not show_players else (self.players_as_str("\n") + '\n')
        return f'Idea: {self.number} ({len(self)}) - {self.name}\n{players}'
