import random
from typing import List

from discord.ext import commands

from game_set import GameSet
from player import Player
from round import Round


class Tournament:
    def __init__(self):
        self.next_id = 0
        self.is_reg_open = True
        self.players = []

        # Stores the rounds
        # NB: Used for display purposes only during registration
        self.rounds_ = None

    def register(self, user_fq, user_display):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed')

        if user_fq in self:
            raise commands.errors.UserInputError(f'{user_display} already exists')
        self.invalidate_computed_values()
        player = Player(user_fq, user_display, self.get_id())
        self.players.append(player)
        return player.id_

    def unregister(self, user_fq, user_display):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed')

        if user_fq not in self:
            raise commands.errors.UserInputError(f'{user_display} was not registered')
        self.invalidate_computed_values()
        for i, player in enumerate(self.players):
            if player.fq == user_fq:
                self.players = self.players[:i] + self.players[i + 1:]
                return player.id_
        raise Exception('Code should never reach here player should have been found to unregister')

    def shuffle(self):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed. Shuffle not allowed.')
        self.invalidate_computed_values()
        random.shuffle(self.players)

    def __contains__(self, fq):
        for player in self.players:
            if player.fq == fq:
                return True
        return False

    def get_id(self):
        self.next_id += 1
        return self.next_id

    def start(self, rounds_best_out_of: List[int]):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Tournament already started!')

        self.calc_all_rounds()
        if len(rounds_best_out_of) != len(self.rounds):
            raise commands.errors.UserInputError(
                f'Number of rounds does not match count of number passed.\n'
                f'Rounds {len(self.rounds)}. Count of numbers passed: {len(rounds_best_out_of)}')

        for best_out_of, round in zip(rounds_best_out_of, self.rounds):
            round.best_out_of = best_out_of

    @property
    def rounds(self):
        if self.rounds_ is None:
            round_ = Round()
            self.rounds_ = [round_]
            p1 = None
            for player in self.players:
                if p1 is None:
                    p1 = player
                else:
                    round_.add(p1, player)
                    p1 = None

            # If there were an odd number of players and one is left over
            # put them into a game by themselves (auto win)
            if p1 is not None:
                round_.add(p1)
        return self.rounds_

    def count(self):
        player_count = len(self.players)
        if self.is_reg_open:
            self.calc_all_rounds()
        round_count = len(self.rounds)
        return player_count, round_count

    def count_as_str(self):
        player_count, round_count = self.count()
        return f'There are {player_count} players registered forming  {round_count} rounds'

    def status(self):
        return f'**Status Report**:\nRegistration: {"open" if self.is_reg_open else "closed"}\n' \
               f'{self.count_as_str()}'

    def invalidate_computed_values(self):
        self.rounds_ = None
        GameSet.reset_id_count()

    def __str__(self):
        result = ""
        for i, round_ in enumerate(self.rounds):
            result += f'--- Round {i + 1} ---\n{round_}\n'
        return result

    def calc_all_rounds(self):
        """
        Repeatedly calculate next round until finals
        - favoring byes on front when rounds count is even
        - and byes at end when round count is odd
        """
        rounds = self.rounds
        while rounds[-1].games_count > 1:
            last_round = rounds[-1]
            new_round = Round()
            if last_round.games_count % 2 != 0 and len(rounds) % 2 == 0:
                # Has bye and is round count is even put bye at the front
                new_round.add(last_round[0].to_player())
                start = 1  # start from next game
            else:
                start = 0  # start from first game bye will go at end
            p1 = None
            for i in range(start, last_round.games_count):
                if p1 is None:
                    p1 = last_round[i].to_player()
                else:
                    new_round.add(p1, last_round[i].to_player())
                    p1 = None
            if p1 is not None:
                # Bye has to go at end
                assert last_round.games_count % 2 != 0
                assert len(rounds) % 2 != 0
                new_round.add(p1)
            rounds.append(new_round)
