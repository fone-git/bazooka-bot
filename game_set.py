from player import Player


class GameSet:
    next_id = 1  # Global counter for game IDs (Reset when rounds is invalidated

    def __init__(self, p1, p2):
        self.game_id = self.new_game_id()
        self.p1 = p1
        self.p2 = p2
        self.p1_score = 0
        self.p2_score = 0

    def __str__(self):
        return f'g{self.game_id}: {self.p1} ({self.p1_score}) vs {self.p2} ({self.p2_score})'

    def to_player(self):
        """
        Creates a player object to represent the unknown winner of this game
        """
        return Player("", f'Winner g{self.game_id}', "?")

    @classmethod
    def reset_id_count(cls):
        cls.next_id = 1

    @classmethod
    def new_game_id(cls):
        result = cls.next_id
        cls.next_id += 1
        return result
