from dataclasses import dataclass
from typing import Set

from bot.common.player import Player


@dataclass
class ScoreSet:
    score: int
    players: Set[Player]

    def add_player(self, player: Player):
        self.players.add(player)

    def remove_player(self, player: Player):
        self.players.remove(player)

    def has_players(self):
        return len(self.players) > 0

    def __str__(self):
        return f'{self.score} - {self.players}'
