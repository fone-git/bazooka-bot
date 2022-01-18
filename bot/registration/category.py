from dataclasses import dataclass

from bot.common.player_list import PlayerList


@dataclass
class Category(PlayerList):
    number: int = 1
    _name: str = 'Default'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._invalidate_calculated()

    def get_str_rep(self):
        players = self.players_as_str("\n")
        return f'Idea: {self.number} - {self.name} ({len(self)})\n' \
               f'{players}\n'
