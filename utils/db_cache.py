class DBCache:
    """
    Provides a write cache for dict like databases.
    ASSUMES: Database is not updated elsewhere and does not use
    coroutines so expected that calls are blocking so there are not race
    conditions to be considered.
    """

    def __init__(self, db_backing: dict):
        self.db_backing = db_backing
        self.cache = {}

    def __contains__(self, item):
        return item in self.cache or item in self.db_backing

    def __getitem__(self, item):
        if item in self.cache:
            return self.cache[item]
        else:
            return self.db_backing[item]

    def __setitem__(self, key, value):
        self.db_backing[key] = value

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return self.db_backing.get(key)
