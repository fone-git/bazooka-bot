from utils.log import log


def get_db() -> dict:
    """
    Access to REPL DB
    :return:
    """
    try:
        from replit import db
        log("Imported access to REPL DB")
    except ModuleNotFoundError:
        db = {}  # For working locally (Assume empty db)
        log("Unable to get REPL DB Using Local dict")
    return db
