import typing as tp
from time import time

from .scope import scope_mgr


class Timer:
    def __init__(self) -> None:
        self._instant_time = time()
        self._scoped_times = {'global': self._instant_time}

    def current_time(self) -> float:
        return time()

    def update_time(self) -> tp.Tuple[float, float]:
        old, new = self._instant_time, time()
        self._instant_time = new
        return old, new

    def update_scoped_time(self) -> tp.Tuple[float, float]:
        key = scope_mgr.current_scope or 'global'
        old, new = self._scoped_times[key], time()
        self._scoped_times[key] = new
        return old, new

    def init_scope_timer(self, scope_name: str) -> None:
        self._scoped_times[scope_name] = time()

    def reset(self) -> None:
        self._instant_time = time()
        if scope_mgr.current_scope:
            self._scoped_times[scope_mgr.current_scope] = self._instant_time
        else:  # global
            self._scoped_times.clear()
            self._scoped_times['global'] = self._instant_time


timer = Timer()
