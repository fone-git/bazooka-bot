"""
Simple script to clear out retry info
"""
import logging

from opylib.db_cache import DBCache
from opylib.log import log, setup_log
from opylib.replit_support import get_db

from utils.connect_manager import ConnectManager


def do_nothing():
    pass


def main():
    setup_log(None, only_std_out=True)
    db = DBCache(get_db(), purge_loglevel=logging.INFO)
    log(ConnectManager.status(db))
    ConnectManager.init_last_conn_fail_info(db)
    db.purge()
    log(f"Connections Allowed Again")


if __name__ == '__main__':
    main()
