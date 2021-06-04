from dataclasses import dataclass, field

from bot.common.player_list import PlayerList


@dataclass
class Category(PlayerList):
    number: int = 1
    name: str = 'General'
    _name: str = field(init=False, repr=False)

    def __post_init__(self):
        # Just so that we don't create the property a second time.
        if not isinstance(getattr(Category, "name", False), property):
            self._name = self.name
            Category.name = property(Category._get_name, Category._set_name)

    def _get_name(self):
        return self._name

    def _set_name(self, val):
        self._name = val
        self._invalidate_calculated()

    def get_str_rep(self):
        players = self.players_as_str("\n")
        return f'Category: {self.number} - {self.name} ({len(self)})\n' \
               f'{players}\n'
