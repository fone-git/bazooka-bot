from game_set import GameSet


class Round:
    def __init__(self):
        self.game_sets = []
        self.best_of = None

    def add(self, p1, p2=None):
        self.game_sets.append(GameSet(p1, p2))

    def __getitem__(self, key):
        return self.game_sets[key]

    @property
    def games_count(self):
        return len(self.game_sets)

    def __str__(self):
        result = ""
        for game_set in self.game_sets:
            result += f'{game_set}\n'

        return result
