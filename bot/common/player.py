from typing import Any, Union

import discord


class Player:
    """
    Represents a discord User as a Player.
    Uses the users discord ID. And this field is immutable to support
    hashing and equality checks.

    WARNING: Two players with different display names but the same ID are
    considered equal and ALL players with ID "None" are considered equal
    """

    def __init__(self, id_: Union[int, None], display: str, disp_id: Any, *,
                 is_dummy: bool = False):
        self._id = id_
        self.display = display
        self.disp_id = disp_id
        self.is_dummy = is_dummy  # Used to mark place holders

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.id == other.id
        return NotImplemented

    def __hash__(self):
        return hash(self.id)

    @property
    def mention(self):
        if self.id is None:
            raise Exception(
                f'Unable to mention player without ID saved. Display: {self}')
        return f'<@{self.id}>'

    def __str__(self):
        result = '' if self.disp_id is None else f'{self.disp_id} - '
        result += f'{self.display}'
        return result

    @staticmethod
    def get_player_from_user(user: discord.User):
        # TODO Add a converter to use this function to auto convert to player
        return Player(user.id, user.display_name, None)
