from collections import OrderedDict
from typing import List, Union

from discord.ext import commands

from bot.common.player import Player
from bot.registration.category import Category


class Registration:
    def __init__(self, are_mutually_exclusive_events: bool = False):
        self.message = ""
        self.categories: OrderedDict[int, Category] = OrderedDict(
            {1: Category(number=1)})
        self.max_cat_num = 1
        self.are_mutually_exclusive_events = are_mutually_exclusive_events
        self.player_cat_dict = {}

    def category_new(self, name: str, number: int):
        if number < 0:
            number = self.max_cat_num + 1
            self.max_cat_num = number

        if number > self.max_cat_num:
            self.max_cat_num = number

        self.confirm_cat_exists(number, False)

        self.categories[number] = Category(number=number, name=name)
        self._sort()

    def category_remove(self, number: int):
        self.confirm_cat_exists(number, True)
        if len(self.categories) == 1:
            raise commands.errors.UserInputError(
                'Unable to remove only one category left')
        if self.are_mutually_exclusive_events:
            # Clear out players from dict
            for player in self.categories[number]:
                self.player_cat_dict.pop(player)
        result = self.categories.pop(number).name
        if number == self.max_cat_num:
            # Max removed find new max
            self.max_cat_num = max(self.categories.keys())
        return result

    def category_rename(self, number: int, new_name: str):
        self.confirm_cat_exists(number, True)
        self.categories[number].name = new_name

    def resolve_cat_number(self,
                           cat_number:
                           Union[int, str]) -> Union[int, List[int]]:
        """
        Resolves an input into a valid category number or list of category 
        numbers.
        - None: Only available category or an error
        - "all": If events are not mutually exclusive returns all category 
                numbers
        - single int: Returns the input
        :param cat_number: The value to be resolved
        :return: A valid category number or list of category numbers
        """
        if cat_number is None:
            if len(self.categories) == 1:
                assert self.max_cat_num in self.categories
                return self.max_cat_num
            else:
                raise commands.errors.UserInputError(
                    'Idea number required when there is more than one idea')
        else:
            if isinstance(cat_number, str):
                if cat_number == 'all':
                    if self.are_mutually_exclusive_events:
                        raise commands.errors.UserInputError(
                            f'"all" only allowed if events are not mutually '
                            f'exclusive')
                    else:
                        return [x for x in self.categories.keys()]
                else:
                    raise commands.errors.UserInputError(
                        f'Expected a idea NUMBER or "all" but got '
                        f'{cat_number}')
            else:
                # Only other expected type is an int
                assert isinstance(cat_number, int)
                return cat_number

    def register(self, player: Player, cat_number: Union[int, str, None]):
        cat_number = self.resolve_cat_number(cat_number)
        if isinstance(cat_number, List):
            for x in cat_number:
                self.register(player, x)
            return  # Do nothing more already called
        self.confirm_cat_exists(cat_number, True)
        if self.are_mutually_exclusive_events:
            # Check if player is already registered
            if player in self.player_cat_dict:
                self.unregister(player, self.player_cat_dict[player])
            self.player_cat_dict[player] = cat_number
        self.categories[cat_number].add(player)

    def unregister(self, player: Player, cat_number: Union[int, str, None]):
        cat_number = self.resolve_cat_number(cat_number)
        if isinstance(cat_number, List):
            for x in cat_number:
                self.unregister(player, x)
            return  # Do nothing more already called

        self.confirm_cat_exists(cat_number, True)
        self.categories[cat_number].remove(player)
        self.player_cat_dict.pop(player, "No Exception If Not Present")

    def set_msg(self, msg: str):
        self.message = msg if msg is not None else ''

    def __str__(self):

        total_players = 0
        vote_type = "SINGLE VOTE" \
            if self.are_mutually_exclusive_events else \
            "MULTIPLE VOTES"
        result = f'UNRANKED IDEAS ' \
                 f'({vote_type}' \
                 f' ALLOWED)\n{self.message}\n\n'
        for key in self.categories.keys():
            total_players += len(self.categories[key])
            result += f'{self.categories[key]}\n'

        result += f'Total Number of Players: {total_players}'
        return result

    def confirm_cat_exists(self, number: int, should_exist: bool):
        """
        Checks if a category exists or not based on the number and raises an
        exception if the expectation is not met with a suitable error message
        :param number: The number of the category to find
        :param should_exist: if true category must exist or exception is
        raised else exception is raised if the category does not exist
        """
        if (number in self.categories) != should_exist:
            raise commands.errors.UserInputError(
                f'Idea {number} '
                f'{"does not" if should_exist else "already"} exists')

    def _sort(self):
        # Ignored because of error in type checker
        # noinspection PyTypeChecker
        self.categories = OrderedDict(sorted(self.categories.items()))
