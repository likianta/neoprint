import typing as tp
from contextlib import contextmanager
from uuid import uuid4


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
    if not name:
        name = str(uuid4())[:8]
    scope_mgr.push(name)
    try:
        yield name
    finally:
        scope_mgr.pop(name)
