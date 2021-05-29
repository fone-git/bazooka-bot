# Couldn't use shelve because close is never called in client code
import logging
from os import path

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class DictPersistent:
    """
    Simple dict that reads from a file on object creation and writes to the
    file each time a value is set. (Mutated objects not written to disk)

    NB: Reads are cheap because it is kept in memory but every set writes
    everything to disk so they are expensive.
    """

    def __init__(self, file_name: str = 'dict_persistent.yaml'):
        self.filename = file_name
        if not path.exists(file_name):
            with open(file_name, "x"):
                pass  # create the file (fail early if unable to create)
            self.data = {}
        else:
            with open(file_name, 'r') as f:
                self.data = yaml.load(f, Loader=Loader)
            if not isinstance(self.data, dict):
                logging.log(logging.ERROR,
                            f'Data loaded from {file_name} was not a dict. '
                            f'Reverting to empty dict')
                self.data = {}

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def get(self, key):
        return self.data.get(key)

    def keys(self):
        return self.data.keys()

    def pop(self, key):
        result = self.data.pop(key)
        self.save()
        return result

    def save(self):
        with open(self.filename, 'w') as f:
            f.write(yaml.dump(self.data, Dumper=Dumper))
