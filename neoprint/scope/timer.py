from time import time
from .scope import scope_mgr


class Timer:
    def __init__(self) -> None:
        self._scoped_times = {'global': time()}

    def reset(self, frame_id: str) -> None:
        if frame_id == 'global':
            self._scoped_times.clear()
            self._scoped_times['global'] = time()
        else:
            self._scoped_times[frame_id] = time()

    def start_timer(self, frame_id: str) -> None:
        key = (
            'global'
            if frame_id == 'global'
            else (scope_mgr.current_scope or frame_id)
        )
        self._scoped_times[key] = time()

    def stop_timer(self, frame_id: str) -> float:
        key = (
            'global'
            if frame_id == 'global'
            else (scope_mgr.current_scope or frame_id)
        )
        out = time() - self._scoped_times[key]
        self._scoped_times[key] = time()
        return out


timer = Timer()
