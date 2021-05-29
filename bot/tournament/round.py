from typing import List

from bot.common.player import Player
from bot.tournament.game_set import GameSet


class Round:
    def __init__(self):
        self.game_sets: List[GameSet] = []
        self.best_out_of = None

    def add(self, p1: Player, p2: Player = None):
        self.game_sets.append(GameSet(p1, p2, self))

    def __getitem__(self, key) -> GameSet:
        return self.game_sets[key]

    @property
    def games_count(self):
        return len(self.game_sets)

    def __str__(self):
        result = '' if self.best_out_of is None \
            else f'Best out of: {self.best_out_of}\n'
        for game_set in self.game_sets:
            result += f'{game_set}\n'

        return result
