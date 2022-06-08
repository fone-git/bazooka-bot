"""
Simple script to clear out retry info
"""
from opylib.log import log, setup_log

from utils.connect_manager import ConnectManager
from utils.db_cache import DBCache
from utils.repl_support import get_db


def do_nothing():
    pass


def main():
    setup_log(None, only_std_out=True)
    db = DBCache(get_db())
    log(ConnectManager.status(db))
    ConnectManager.init_last_conn_fail_info(db)
    db.purge()
    log(f"Connections Allowed Again")


if __name__ == '__main__':
    main()
