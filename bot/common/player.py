from typing import Any, Union

import discord


class Player:
    def __init__(self, id_: Union[int, None], display: str, disp_id: Any, *,
                 is_dummy: bool = False):
        self.id = id_
        self.display = display
        self.disp_id = disp_id
        self.is_dummy = is_dummy  # Used to mark place holders

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
        return Player(user.id, user.display_name, None)
