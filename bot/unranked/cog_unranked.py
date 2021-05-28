from bot.common.cog_common import CogCommon
from conf import Conf

from utils import db_cache

conf = Conf.Unranked
"""Map class with setting for this cog to variable"""


class CogUnranked(CogCommon, name='Unranked'):
    def __init__(self, db: db_cache):
        super().__init__(db, conf=conf)

    def load(self):
        pass

    def save(self):
        pass
