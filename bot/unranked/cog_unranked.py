from bot.common.cog_common import CogCommon
from conf import Conf

# Map class with setting for this cog to variable
conf = Conf.Unranked


class CogUnranked(CogCommon, name='Unranked'):
    def __init__(self, db: dict):
        super().__init__(db, conf=conf)

    def load(self):
        pass

    def save(self):
        pass
