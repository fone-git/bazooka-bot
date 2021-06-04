from dataclasses import dataclass

from bot.common.player_list import PlayerList


@dataclass
class ScoreSet(PlayerList):
    score: int = 0

    def get_str_rep(self):
        return f'{self.score} WINS - {self.players_as_str()}'
