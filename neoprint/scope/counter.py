from collections import defaultdict
from random import choices

from .scope import scope_mgr
from ..frame import FrameInfo


class Counter:
    def __init__(self) -> None:
        self._colors = {}
        self._global_index = 0
        self._scoped_indexes = defaultdict(int)

    def get_color_by_frame(self, frame: FrameInfo) -> str:
        if frame.id not in self._colors:
            # random bright color
            # https://stackoverflow.com/questions/43437309
            self._colors[frame.id] = '#' + ''.join(choices('89abcdef', k=6))
        return self._colors[frame.id]

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
