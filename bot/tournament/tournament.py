import logging
import random
from typing import Iterable, List, Union

from discord import Embed
from discord.ext import commands

from bot.common.player import Player
from bot.tournament.game_set import GameSet
from bot.tournament.round import Round
from conf import Conf
from utils.log import log
from utils.misc import is_power_of_2


class Tournament:
    def __init__(self):
        # TODO Add a setting to control type of tournament
        self.next_id = 0
        self.is_reg_open = True
        self.players = []

        # Stores the computed rounds for display purposes to prevent
        # redundant recalculation
        self.rounds_: Union[None, Iterable[Round]] = None

        # Dict of next match player is carded to play if any
        # NB: maybe be overwritten repeatedly during registration as
        #   match ups can be changed at that point
        self.players_map = {}

    def register(self, player: Player):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed')

        if player.id in self:
            raise commands.errors.UserInputError(
                f'{player} already exists')
        assert player.disp_id is None
        player.disp_id = self.get_id()
        self.players.append(player)
        self.invalidate_computed_values()

    def unregister(self, player: Player):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(f'Registration is closed')

        if player.id not in self:
            raise commands.errors.UserInputError(
                f'{player} was not registered')
        for i, p in enumerate(self.players):
            if player.id == p.id:
                self.players = self.players[:i] + self.players[i + 1:]
                self.invalidate_computed_values()
                return p.disp_id
        raise Exception(
            'Code should never reach here player should have been found to '
            'unregister')

    def shuffle(self):
        if not self.is_reg_open:
            raise commands.errors.UserInputError(
                f'Registration is closed. Shuffle not allowed.')
        random.shuffle(self.players)
        self.invalidate_computed_values()

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
            raise commands.errors.UserInputError(
                f'Tournament already started!')

        self.calc_all_rounds()
        if len(rounds_best_out_of) != len(self.rounds):
            raise commands.errors.UserInputError(
                f'Number of rounds does not match count of number passed.\n'
                f'Rounds {len(self.rounds)}. Count of numbers passed: '
                f'{len(rounds_best_out_of)}')

        for best_out_of, round_ in zip(rounds_best_out_of, self.rounds):
            round_.best_out_of = best_out_of

        # Check for a bye to be advanced (Can only be on last game
        # because the first count is odd and rules says odd is at end)
        if self.rounds[0][-1].p2 is None:
            player = self.rounds[0][-1].p1
            ind = 0
            game = self.rounds[0][-1]
            self.advance_player_ind(player, game, ind)
        self.is_reg_open = False

    def reopen_registration(self):
        if self.is_reg_open:
            raise commands.errors.UserInputError(
                f'Registration was already open!')
        self.is_reg_open = True
        self.invalidate_computed_values()

    @property
    def rounds(self) -> List[Round]:
        if self.rounds_ is None:
            round_ = Round()
            self.rounds_ = [round_]
            p1: Union[Player, None] = None
            for player in self.players:
                if p1 is None:
                    p1 = player
                else:
                    round_.add(p1, player)
                    self.players_map[p1.id] = round_[-1]
                    self.players_map[player.id] = round_[-1]
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
        return f'There are {player_count} players registered forming  ' \
               f'{round_count} rounds'

    def status(self):
        return f'**Status Report**:\n' \
               f'Registration: {"open" if self.is_reg_open else "closed"}\n' \
               f'{self.count_as_str()}'

    def invalidate_computed_values(self):
        self.rounds_ = None
        GameSet.reset_id_count()
        self.players_map = {}
        log('[Tournament] Computed Values Invalidated', logging.DEBUG)
        self.calc_all_rounds()

    def win(self, player: Player, qty):
        game: GameSet = self.players_map.get(player.id)

        if game is None:
            raise commands.errors.UserInputError(
                f"Didn't find an active game for {player}")

        if game.has_dummy_player():
            raise commands.errors.UserInputError(
                f"This game doesn't appear to have two players - {game}")

        if player.id == game.p1.id:
            win_ind = 0
            lose_ind = 1
            player = game.p1
        elif player.id == game.p2.id:
            win_ind = 1
            lose_ind = 0
            player = game.p2
        else:
            raise Exception(
                f"Player found from dict but didn't match either player in "
                f"game {game.game_id}")

        game.scores[win_ind] += qty
        if game.is_won():
            # Remove loser from dict and advance winner
            self.players_map.pop(game.players[lose_ind].id)
            return self.advance_player_ind(player, game, win_ind)
        return f'{qty} point(s) added to {player} for {game}'

    def __str__(self):
        result = ""
        for i, round_ in enumerate(self.rounds):
            result += f'--- Round {i + 1} ---\n{round_}\n'

        # Check for 3rd place match
        third_place_match = self.get_third_place_match()
        if third_place_match is not None:
            result += f'\nThird Place Match:\n{third_place_match}\n'
        return result

    def calc_all_rounds(self):
        """
        Repeatedly calculate next round until finals
        - favoring byes on front on even rounds numbers
        - and byes at end on odd round numbers
        :return: True if changes were made else False
        """
        changes_made = False
        rounds = self.rounds
        while rounds[-1].games_count > 1:
            changes_made = True  # Register that changes were made
            log(f'[Tournament] Calculating Round {len(rounds) + 1}',
                logging.DEBUG)
            last_round = rounds[-1]
            new_round = Round()
            if last_round.games_count % 2 != 0 and (len(rounds) + 1) % 2 == 0:
                # Plus 1 to get the number for this round
                # Has bye and round number is even put bye at the front
                new_round.add(last_round[0].winner_player())
                last_round[0].win_next_game = new_round[-1]
                last_round[0].win_next_game_player_ind = 0
                start = 1  # start from next game
            else:
                start = 0  # start from first game bye will go at end
            g1: Union[None, GameSet] = None
            for i in range(start, last_round.games_count):
                if g1 is None:
                    g1 = last_round[i]
                else:
                    new_round.add(g1.winner_player(),
                                  last_round[i].winner_player())
                    g1.win_next_game = new_round[-1]
                    g1.win_next_game_player_ind = 0
                    last_round[i].win_next_game = new_round[-1]
                    last_round[i].win_next_game_player_ind = 1
                    g1 = None
            if g1 is not None:
                # Bye has to go at end
                assert last_round.games_count % 2 != 0
                assert (len(rounds) + 1) % 2 != 0
                # Plus 1 to get the number for this round
                new_round.add(g1.winner_player())
                g1.win_next_game = new_round[-1]
                g1.win_next_game_player_ind = 0
            rounds.append(new_round)
        # TODO Add setting to control if 3rd place match should be held
        if changes_made:
            # Set Finals
            assert rounds[-1].games_count == 1
            rounds[-1][0].is_finals = True

            # Create 3rd place match
            self.add_third_place_match()
        return changes_made

    def add_third_place_match(self):
        if len(self.rounds) < 2:
            return  # Not enough rounds do anything

        assert self.rounds[-2].games_count == 2

        # Get games that feed into the match
        g1: GameSet = self.rounds[-2][0]
        g2: GameSet = self.rounds[-2][1]

        if g1.lose_next_game is not None:
            log('[Tournament] Seems there is already a match for losers of '
                'semi finals ABORTING creating 3rd place match',
                logging.WARNING)
            return

        third_place_match = GameSet(g1.loser_player(), g2.loser_player(),
                                    self.rounds[-1])
        g1.lose_next_game = third_place_match
        g1.lose_next_game_player_ind = 0
        g2.lose_next_game = third_place_match
        g2.lose_next_game_player_ind = 1

    def advance_player_ind(self, player_win: Player, game: GameSet,
                           win_ind: int):
        result = ''
        if game.win_next_game is None:

            # if winner does not advance expected that loser does not advance
            assert game.lose_next_game is None

            if game.is_finals:
                return f'CONGRATULATIONS {player_win.mention} has won the ' \
                       f'tournament!!!'
            else:
                # Example use case is 3rd place match
                return f'{player_win.mention} TAKES [{game}]'
        game.win_next_game.players[game.win_next_game_player_ind] = \
            game.players[win_ind]
        self.players_map[player_win.id] = game.win_next_game

        lose_ind = (win_ind + 1) % 2
        if game.lose_next_game is not None:
            player_lose = game.players[lose_ind]
            if player_lose is not None:
                game.lose_next_game.players[game.lose_next_game_player_ind] = \
                    player_lose
                self.players_map[player_lose.id] = game.lose_next_game
                result = f'\n\n-- AND --\n\n{player_lose.mention} moves to [' \
                         f'{game.lose_next_game}]'

        # Check if the next game is a bye
        # ASSUMPTION: expected max 1 bye before having to play again. So
        # doesn't check if next game is a bye
        opponent_ind = (game.win_next_game_player_ind + 1) % 2
        if game.win_next_game.players[opponent_ind] is None:
            new_ind = game.win_next_game.win_next_game_player_ind
            game.win_next_game.win_next_game.players[new_ind] = game.players[
                win_ind]
            self.players_map[player_win.id] = game.win_next_game.win_next_game
            game = game.win_next_game  # Advance pointer for print out
        result = f'{player_win.mention} TAKES [{game}] and ADVANCES to [' \
                 f'{game.win_next_game}]{result}'
        return result

    def as_html(self):
        # TODO Find a way to include round number and best out of

        if len(self.players) == 0:
            return '<h1> No one is registered yet </h1>'

        result = ''
        for i, round_ in enumerate(self.rounds):
            result += f'<ul class="round round-{i + 1}">'

            count_added = 0
            for game in round_:
                result += f'<li class="spacer">&nbsp;</li>' \
                          f'<li class="game game-top ' \
                          f'{game.is_p1_winner()}">{game.p1}' \
                          f'<span>{game.p1_score}</span></li>' \
                          f'<li class="game game-spacer">Game ' \
                          f'{game.game_id}</li>' \
                          f'<li class="game game-bottom ' \
                          f'{game.is_p2_winner()}">{game.p2}' \
                          f'<span>{game.p2_score}</span></li>'
                count_added += 1
            while not is_power_of_2(count_added):
                result += f'<li class="spacer">&nbsp;</li>' \
                          f'<li class="game ' \
                          f'game-top">None<span>&nbsp;</span></li>' \
                          f'<li class="game game-spacer">&nbsp;</li>' \
                          f'<li class="game game-bottom">None' \
                          f'<span>&nbsp;</span></li>'
                count_added += 1

            result += '<li class="spacer">&nbsp;</li> </ul>'

        return result

    def as_embed(self) -> Embed:
        result = Embed(title='HTML Display', color=Conf.EMBED_COLOR,
                       url=Conf.URL)
        if len(self.players) > 0:
            for i, round_ in enumerate(self.rounds):
                result.add_field(name=f'--- Round {i + 1} ---',
                                 value=f'{round_}',
                                 inline=False)

            # Check for 3rd place match
            third_place_match = self.get_third_place_match()
            if third_place_match is not None:
                result.add_field(name=f'Third Place Match',
                                 value=f'{third_place_match}',
                                 inline=False)
        else:
            result.add_field(name='No Rounds', value='No players registered ')
        return result

    def override_set(self, player: Player, game_id: int,
                     player_pos: int):
        if self.is_reg_open:
            raise commands.errors.UserInputError(
                f'Override-Set only available after tournament has started!')

        if player.id not in self:
            raise commands.errors.UserInputError(
                f'{player} not found in tournament')

        player = self.get_player(player.id)
        assert player is not None
        # player should not be non because it passed the contains test

        if 1 > player_pos or 2 < player_pos:
            raise commands.errors.UserInputError(
                f'Player pos expected in range 1-2 but got: {player_pos}')
        player_pos -= 1  # Convert to 0 based value

        game = self.get_game(game_id)
        if game is None:
            raise commands.errors.UserInputError(
                f'Unable to find game with ID: {game_id}')

        # Reset scores
        game.scores[0] = 0
        game.scores[1] = 0

        # Set Player
        game.players[player_pos] = player

        # Update Map
        self.players_map[player.id] = game

        return f'{game}'

    def get_game(self, game_id: int) -> Union[GameSet, None]:
        for round_ in self.rounds:
            for game in round_.game_sets:
                if game.game_id == game_id:
                    return game

        # Last possible place game could be is 3rd place match
        game = self.get_third_place_match()
        if game is not None and game.game_id == game_id:
            return game
        return None

    def get_player(self, user_id) -> Union[Player, None]:
        for player in self.players:
            if player.id == user_id:
                return player
        return None

    def get_third_place_match(self) -> Union[None, GameSet]:
        if len(self.rounds) >= 2:
            # Could be taken from either game. Taking from 1st game of round
            return self.rounds[-2][0].lose_next_game
        else:
            return None
