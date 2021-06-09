from discord.ext import commands

from bot.common.player import Player
from bot.unranked.score_set import ScoreSet
from conf import Conf


class Unranked:
    """
    Maintains players grouped by score (order with score is Nondeterministic).

    INVARIANTS:
        - player_lookup and score_lookup are always in sync.
          either holds all the information by provides quick alternative means
          of quick access depending on the data you start with.
    """

    def __init__(self):
        self.message = ""

        self.player_lookup = {}  # Maps from player to a score_set object
        self.score_lookup = {}  # Maps from score to score_set object

        for i in range(Conf.Unranked.MAX_SCORE + 1):
            self.score_lookup[i] = ScoreSet(score=i)

    def score(self, player: Player, score: int):
        # Validate score
        if not (0 <= score <= Conf.Unranked.MAX_SCORE):
            raise commands.errors.UserInputError(
                f'Score must be in 0 to {Conf.Unranked.MAX_SCORE} but got '
                f'{score}')

        # Check if the player is already in data
        score_set: ScoreSet = self.player_lookup.get(player.id)

        if score_set is not None:
            if score_set.score == score:
                # If same score then exit
                return
            else:
                score_set.remove(player)

        # If code gets to here then the player has been removed (because of
        # different score) or did not already exist.
        #
        # So now simply add the player
        score_set = self.score_lookup[score]
        score_set.add(player)
        self.player_lookup[player.id] = score_set

    def remove_player(self, player):
        score_set: ScoreSet = self.player_lookup.get(player.id)
        if score_set is None:
            raise commands.errors.UserInputError(f'{player} not found!')
        score_set.remove(player)
        self.player_lookup.pop(player.id)

    def set_msg(self, msg):
        self.message = msg

    def __str__(self):
        result = f'UNRANKED CHALLENGE\n{self.message}\n\nRankings:\n'
        if len(self.player_lookup) == 0:
            result += "No scores are recorded right now."
        else:
            for i in range(Conf.Unranked.MAX_SCORE, -1, -1):
                game_set = self.score_lookup[i]
                if game_set.has_players():
                    result += f'{game_set}\n'
        return result
