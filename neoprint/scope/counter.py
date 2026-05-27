from collections import defaultdict
from .scope import scope_mgr


class Counter:
    def __init__(self) -> None:
        self._global_index = 0
        self._scoped_indexes = defaultdict(int)

    def reset(self) -> None:
        self._global_index = 0
        self._scoped_indexes.clear()

    def update_global_index(self) -> int:
        self._global_index += 1
        return self._global_index

    def update_scoped_index(self, uid: str) -> int:
        key = scope_mgr.current_scope or uid
        self._scoped_indexes[key] += 1
        return self._scoped_indexes[key]


counter = Counter()
