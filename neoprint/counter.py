from collections import defaultdict


class Counter:
    def __init__(self):
        self._global_index = 0
        self._scoped_indexes = defaultdict(int)

    def reset(self):
        self._global_index = 0
        self._scoped_indexes.clear()

    def update_global_index(self):
        self._global_index += 1
        return self._global_index

    def update_scoped_index(self, uid: str):
        self._scoped_indexes[uid] += 1
        return self._scoped_indexes[uid]


counter = Counter()
