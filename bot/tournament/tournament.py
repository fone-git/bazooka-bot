import random
from typing import List

from discord.ext import commands

from bot.tournament.game_set import GameSet
from bot.tournament.player import Player
from bot.tournament.round import Round
from utils.misc import is_power_of_2


class Tournament:
    def __init__(self):
        self.next_id = 0
        self.is_reg_open = True
        self.players = []

        # Stores the rounds
        # NB: Used for display purposes only during registration
        self.rounds_ = None

        # Dict of first match with each player
        # only used after start of tournament (before liable to be overwritten at any time)
        self.players_map = {}

    def register(self, user_id, user_display):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed')

        if user_id in self:
            raise commands.errors.UserInputError(f'{user_display} already exists')
        self.invalidate_computed_values()
        player = Player(user_id, user_display, self.get_id())
        self.players.append(player)
        return player.disp_id

    def unregister(self, user_id, user_display):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed')

        if user_id not in self:
            raise commands.errors.UserInputError(f'{user_display} was not registered')
        self.invalidate_computed_values()
        for i, player in enumerate(self.players):
            if player.id == user_id:
                self.players = self.players[:i] + self.players[i + 1:]
                return player.disp_id
        raise Exception('Code should never reach here player should have been found to unregister')

    def shuffle(self):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed. Shuffle not allowed.')
        self.invalidate_computed_values()
        random.shuffle(self.players)

    def __contains__(self, id_):
        for player in self.players:
            if player.id == id_:
                return True
        return False

    def get_id(self):
        self.next_id += 1
        return self.next_id

    def start(self, rounds_best_out_of: List[int]):
        player_count, _ = self.count()
        if player_count == 0:
            raise commands.errors.UserInputError(f'No players registered yet!')

        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Tournament already started!')

        self.calc_all_rounds()
        if len(rounds_best_out_of) != len(self.rounds):
            raise commands.errors.UserInputError(
                f'Number of rounds does not match count of number passed.\n'
                f'Rounds {len(self.rounds)}. Count of numbers passed: {len(rounds_best_out_of)}')

        for best_out_of, round_ in zip(rounds_best_out_of, self.rounds):
            round_.best_out_of = best_out_of

        # Check for a bye to be advanced (Can only be on last game
        # because the first count is odd and rules says odd is at end)
        if self.rounds[0][-1].p2 is None:
            user_id = self.rounds[0][-1].p1.id
            user_display = self.rounds[0][-1].p1.display
            ind = 0
            game = self.rounds[0][-1]
            self.advance_player_ind(user_id, user_display, game, ind)
        self.is_reg_open = False

    def reopen_registration(self):
        if self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration was already open!')
        self.is_reg_open = True
        self.invalidate_computed_values()

    @property
    def rounds(self):
        if self.rounds_ is None:
            round_ = Round()
            self.rounds_ = [round_]
            # noinspection PyTypeChecker
            p1: Player = None
            for player in self.players:
                if p1 is None:
                    p1 = player
                else:
                    round_.add(p1, player)
                    self.players_map[p1.id] = round_[-1]
                    self.players_map[player.id] = round_[-1]
                    # noinspection PyTypeChecker
                    p1 = None

            # If there were an odd number of players and one is left over
            # put them into a game by themselves (auto win)
            if p1 is not None:
                round_.add(p1)
                self.players_map[p1.id] = round_[-1]
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
        self.players_map = {}

    def win(self, user_id, user_display, qty):
        game = self.players_map.get(user_id)
        if game is None:
            raise commands.errors.UserInputError(f"Didn't find an active game for {user_display}")

        if user_id == game.p1.id:
            win_ind = 0
            lose_ind = 1
        elif user_id == game.p2.id:
            win_ind = 1
            lose_ind = 0
        else:
            raise Exception(f"Player found from dict but didn't match either player in game {game.game_id}")

        game.scores[win_ind] += qty
        if game.is_won():
            # Remove loser from dict and advance winner
            self.players_map.pop(game.players[lose_ind].id)
            return self.advance_player_ind(user_id, user_display, game, win_ind)
        return f'{qty} point(s) added to {user_display} for {game}'

    def __str__(self):
        result = ""
        for i, round_ in enumerate(self.rounds):
            result += f'--- Round {i + 1} ---\n{round_}\n'
        return result

    def calc_all_rounds(self):
        """
        Repeatedly calculate next round until finals
        - favoring byes on front on even rounds numbers
        - and byes at end on odd round numbers
        """
        rounds = self.rounds
        while rounds[-1].games_count > 1:
            last_round = rounds[-1]
            new_round = Round()
            if last_round.games_count % 2 != 0 \
                    and (len(rounds) + 1) % 2 == 0:
                # Plus 1 to get the number for this round
                # Has bye and round number is even put bye at the front
                new_round.add(last_round[0].to_player())
                last_round[0].next_game = new_round[-1]
                last_round[0].next_game_player_ind = 0
                start = 1  # start from next game
            else:
                start = 0  # start from first game bye will go at end
            # noinspection PyTypeChecker
            g1: GameSet = None
            for i in range(start, last_round.games_count):
                if g1 is None:
                    g1 = last_round[i]
                else:
                    new_round.add(g1.to_player(), last_round[i].to_player())
                    g1.next_game = new_round[-1]
                    g1.next_game_player_ind = 0
                    last_round[i].next_game = new_round[-1]
                    last_round[i].next_game_player_ind = 1
                    # noinspection PyTypeChecker
                    g1 = None
            if g1 is not None:
                # Bye has to go at end
                assert last_round.games_count % 2 != 0
                assert (len(rounds) + 1) % 2 != 0
                # Plus 1 to get the number for this round
                new_round.add(g1.to_player())
                g1.next_game = new_round[-1]
                g1.next_game_player_ind = 0
            rounds.append(new_round)

    def advance_player_ind(self, user_id, user_display, game, win_ind):
        if game.next_game is None:
            return f'CONGRATULATIONS {user_display} has won the tournament!!!'
        game.next_game.players[game.next_game_player_ind] = game.players[win_ind]
        self.players_map[user_id] = game.next_game
        other_ind = (win_ind + 1) % 2

        # Check if the next game is a bye
        # ASSUMPTION: expected max 1 bye before having to play again. So doesn't check if next game is a bye
        if game.next_game.players[other_ind] is None:
            new_ind = game.next_game.next_game_player_ind
            game.next_game.next_game.players[new_ind] = game.players[win_ind]
            self.players_map[user_id] = game.next_game.next_game
            game = game.next_game
        return f'{user_display} TAKES [{game}] and ADVANCES to [{game.next_game}]'

    def as_html(self):
        # TODO Find a way to include round number and best out of

        # TODO fix display of tournaments with rounds that do not have a number of players that is a power of 2

        if len(self.players) == 0:
            return '<h1> No one is registered yet </h1>'

        result = ''
        for i, round_ in enumerate(self.rounds):
            result += f'<ul class="round round-{i + 1}">'

            count_added = 0
            for game in round_:
                result += f'<li class="spacer">&nbsp;</li>' \
                          f'<li class="game game-top {game.is_p1_winner()}">{game.p1}' \
                          f'<span>{game.p1_score}</span></li>' \
                          f'<li class="game game-spacer">Game {game.game_id}</li>' \
                          f'<li class="game game-bottom {game.is_p2_winner()}">{game.p2}' \
                          f'<span>{game.p2_score}</span></li>'
                count_added += 1
            while not is_power_of_2(count_added):
                result += f'<li class="spacer">&nbsp;</li>' \
                          f'<li class="game game-top">None<span>&nbsp;</span></li>' \
                          f'<li class="game game-spacer">&nbsp;</li>' \
                          f'<li class="game game-bottom">None<span>&nbsp;</span></li>'
                count_added += 1

            result += '<li class="spacer">&nbsp;</li> </ul>'

        return result
