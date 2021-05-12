from game_set import GameSet


class Round:
    def __init__(self):
        self.game_sets = []

    def add(self, p1, p2=None):
        self.game_sets.append(GameSet(p1, p2))

    def __str__(self):
        result = ""
        for game_set in self.game_sets:
            result += f'{game_set}\n'

        return result
