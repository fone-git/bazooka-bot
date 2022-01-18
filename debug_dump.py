"""
Dumps each key in the db to separate file in one folder for debugging
"""

from conf import Conf
from utils.misc import debug_dump
from utils.repl_support import get_db

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main():
    db = get_db()
    debug_dump(Conf.DEBUG_DUMP_FOLDER, db)
    print("Debug Dump Completed")


if __name__ == '__main__':
    main()
