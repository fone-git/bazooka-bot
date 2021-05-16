"""
Simple script to load the export into the DB
"""
import yaml

from conf import Conf
from utils.repl_support import get_db

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main():
    with open(Conf.EXPORT_FILE_NAME, 'r') as f:
        data = yaml.load(f, Loader=Loader)
    db = get_db()
    for key in data.keys():
        db[key] = data[key]
    print('Import Completed')


if __name__ == '__main__':
    main()
