from typing import Any


class Player:
    def __init__(self, id_: int, display: str, disp_id: Any, *,
                 is_dummy: bool = False):
        self.id = id_
        self.display = display
        self.disp_id = disp_id
        self.is_dummy = is_dummy  # Used to mark place holders

    @property
    def mention(self):
        return f'<@{self.id}>'

    def __str__(self):
        return f'{self.disp_id} - {self.display}'
