from typing import List, Union

from discord.ext import commands

from bot.common.player import Player
from bot.registration.category import Category


class Registration:
    def __init__(self):
        self.message = ""
        self.categories = {1: Category(number=1)}
        self.max_cat_num = 1

    def category_new(self, name: str, number: int):
        if number < 0:
            number = self.max_cat_num + 1
            self.max_cat_num = number

        self.confirm_cat_exists(number, False)

        self.categories[number] = Category(number=number, name=name)

    def category_remove(self, number: int):
        self.confirm_cat_exists(number, True)
        if len(self.categories) == 1:
            raise commands.errors.UserInputError(
                'Unable to remove only one category left')
        self.categories.pop(number)
        if number == self.max_cat_num:
            # Max removed find new max
            self.max_cat_num = max(self.categories.keys())

    def category_rename(self, number: int, new_name: str):
        self.confirm_cat_exists(number, True)
        self.categories[number].name = new_name

    def resolve_cat_number(self,
                           cat_number:
                           Union[int, str]) -> Union[int, List[int]]:
        if cat_number is None:
            if len(self.categories) == 1:
                assert self.max_cat_num in self.categories
                return self.max_cat_num
            else:
                raise commands.errors.UserInputError(
                    'Category number required when there is more than one '
                    'category')
        else:
            if isinstance(cat_number, str):
                if cat_number == 'all':
                    return [x for x in self.categories.keys()]
                else:
                    raise commands.errors.UserInputError(
                        f'Expected a category NUMBER or "all" but got '
                        f'{cat_number}')
            else:
                # Only other expected type is an int
                assert isinstance(cat_number, int)
                return cat_number

    def register(self, player: Player, cat_number: Union[int, str]):
        cat_number = self.resolve_cat_number(cat_number)
        if isinstance(cat_number, List):
            for x in cat_number:
                self.register(player, x)
            return  # Do nothing more already called
        self.confirm_cat_exists(cat_number, True)
        self.categories[cat_number].add(player)

    def unregister(self, player: Player, cat_number: Union[int, str]):
        cat_number = self.resolve_cat_number(cat_number)
        if isinstance(cat_number, List):
            for x in cat_number:
                self.unregister(player, x)
            return  # Do nothing more already called

        self.confirm_cat_exists(cat_number, True)
        self.categories[cat_number].remove(player)

    def set_msg(self, msg: str):
        self.message = msg

    def __str__(self):

        total_players = 0
        result = f'REGISTRATION\n{self.message}\n\n'
        for key in self.categories.keys():
            total_players += len(self.categories[key])
            result += f'{self.categories[key]}\n'

        result += f'Total Number of Players: {total_players}'
        return result

    def confirm_cat_exists(self, number: int, should_exist: bool):
        """
        Checks if a category exists or not based on the number and raises a
        exception if the expectation is not met with a suitable error message
        :param number: The number of the category to find
        :param should_exist: if true category must exist or exception is
        raised else exception is raised if the category does not exist
        """
        if (number in self.categories) != should_exist:
            raise commands.errors.UserInputError(
                f'Category {number} '
                f'{"does not" if should_exist else "already"} exists')
