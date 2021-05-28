from typing import List, Union

from bot.common.player import Player


class GameSet:
    # Global counter for game IDs (Reset when rounds is invalidated
    next_id = 1

    def __init__(self, p1: Player, p2: Player, round_):
        self.round_ = round_  # Round that the game is in
        self.game_id = self.new_game_id()
        self.players: List[Union[None, Player]] = [p1, p2]
        self.scores = [0, 0]
        self.is_finals = False

        # Stores the game that the winner/loser of this game goes to
        self.win_next_game = None
        self.lose_next_game = None

        # index of the winner/loser of this game in the next game
        self.win_next_game_player_ind = None
        self.lose_next_game_player_ind = None

    def is_won(self):
        for score in self.scores:
            if score > self.round_.best_out_of // 2:
                return True
        return False

    def _is_p_winner(self, score_index: int) -> str:
        return ('winner'
                if
                self.round_.best_out_of is not None
                and self.scores[score_index] > self.round_.best_out_of // 2
                else '')

    def is_p1_winner(self) -> str:
        return self._is_p_winner(0)

    def is_p2_winner(self) -> str:
        return self._is_p_winner(1)

    @property
    def p1(self):
        return self.players[0]

    @property
    def p2(self):
        return self.players[1]

    @property
    def p1_score(self):
        return self.scores[0]

    @property
    def p2_score(self):
        return self.scores[1]

    def __str__(self):
        p1 = f'{self.p1} ({self.p1_score})'
        if self.is_p1_winner():
            p1 = f'**__{p1}__**'
        p2 = f'{self.p2} ({self.p2_score})'
        if self.is_p2_winner():
            p2 = f'**__{p2}__**'
        return f'g{self.game_id}: {p1} vs {p2}'

    def _to_player(self, type_: str) -> Player:
        """
        Creates a player object to represent the unknown <winner/loser> of
        this game
        """
        return Player(-1, f'{type_} of Game {self.game_id}', "?",
                      is_dummy=True)

    def winner_player(self) -> Player:
        return self._to_player('Winner')

    def loser_player(self) -> Player:
        return self._to_player('Loser')

    @classmethod
    def reset_id_count(cls):
        cls.next_id = 1

    @classmethod
    def new_game_id(cls):
        result = cls.next_id
        cls.next_id += 1
        return result

    def has_dummy_player(self):
        return any([True if player is None else player.is_dummy for player in
                    self.players])
