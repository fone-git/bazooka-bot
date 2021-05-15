"""
Simple script to load the export into the DB
"""
from conf import Conf, DBKeys
from utils.repl_support import get_db


def main():
    with open(Conf.EXPORT_FILE_NAME, 'r') as f:
        data = f.read()
    get_db()[DBKeys.TOURNAMENT] = data


if __name__ == '__main__':
    main()
