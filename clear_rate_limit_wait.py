"""
Simple script to clear out retry info
"""

from utils.connect_manager import ConnectManager
from utils.db_cache import DBCache
from utils.repl_support import get_db


def do_nothing():
    pass


def main():
    db = DBCache(get_db())
    print(ConnectManager.status(db))
    ConnectManager.init_last_conn_fail_info(db)
    print("Connections Allowed Again")


if __name__ == '__main__':
    main()
