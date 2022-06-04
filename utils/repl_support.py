from typing import Union

from opylib.log import log

from utils.dict_persistent import DictPersistent


def get_db() -> Union[dict, DictPersistent]:
    """
    Access to REPL DB
    :return:
    """
    try:
        # noinspection PyUnresolvedReferences
        from replit import db
        log("Imported access to REPL DB")
    except ModuleNotFoundError:
        db = DictPersistent()
        log("Unable to get REPL DB Using Local dict")
    return db
