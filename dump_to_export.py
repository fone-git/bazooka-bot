"""
Simple script to clear out data from the DB. Saved to export as precaution
"""

from conf import Conf
from utils.misc import export
from utils.repl_support import get_db

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main():
    db = get_db()
    export(Conf.EXPORT_FILE_NAME, db)
    print("Export Completed")
    keys = [x for x in db.keys()]
    for key in keys:
        db.pop(key)
    print("DB Emptied")


if __name__ == '__main__':
    main()
