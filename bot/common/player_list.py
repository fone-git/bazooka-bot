from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Union

from bot.common.player import Player


@dataclass
class PlayerList:
    """
    Stores a list of players. Does not allow duplicates. Players stored in
    order added.
    """
    players: List[Player] = field(default_factory=list)
    _str_disp: Union[str, None] = None

    def add(self, player: Player):
        """
        Adds the player if there were not already there otherwise does nothing
        :param player: The player to be added
        """
        if player not in self.players:
            self.players.append(player)
            self._invalidate_calculated()

    def remove(self, player: Player):
        """
        Removes the player passed (or does nothing if player does not exist)
        :param player: Player to be removed
        """
        if player in self.players:
            self.players.remove(player)
            self._invalidate_calculated()

    def has_players(self):
        return len(self.players) > 0

    def _invalidate_calculated(self):
        self._str_disp = None

    def __str__(self):
        if self._str_disp is None:
            self._str_disp = self.get_str_rep()
        return self._str_disp

    def players_as_str(self, separator: str = ", "):
        result = ""
        for player in self.players:
            result += f'{player}{separator}'
        if result != "":
            # Crop of trailing separator
            result = result[:-len(separator)]

        return result

    def __len__(self):
        return len(self.players)

    @abstractmethod
    def get_str_rep(self):
        return f'{self.players_as_str()}'
