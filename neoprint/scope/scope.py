import typing as tp
from contextlib import contextmanager
from uuid import uuid4

from ..frame import FrameInfo


class ScopeManager:
    def __init__(self) -> None:
        self._stack = []

    @property
    def current_scope(self) -> tp.Optional[str]:
        return self._stack[-1] if self._stack else None

    def push(self, name: str) -> None:
        self._stack.append(name)

    def pop(self, name: str) -> None:
        assert self._stack.pop() == name


scope_mgr = ScopeManager()


@contextmanager
def scope(name: str = '') -> tp.Generator[str, None, None]:
    from .timer import timer

    if not name:
        name = str(uuid4())[:8]
    scope_mgr.push(name)
    timer.init_scope_timer(name)
    try:
        yield name
    finally:
        scope_mgr.pop(name)


# DELETE?
def frame_to_scope_key(frame: FrameInfo, parent_level: int = 0) -> str:
    target_frame = frame.get_parent(parent_level) if parent_level else frame
    return '{}:{}'.format(target_frame.file_path, target_frame.function_name)
