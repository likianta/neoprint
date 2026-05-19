import uuid
from contextlib import contextmanager
from typing import Dict, Optional


class Counter:
    _global_index: int = 0
    _scoped_indexes: Dict[str, int] = {}
    _line_indexes: Dict[str, int] = {}
    _scope_stack: list = []

    def reset_all(self) -> None:
        self._global_index = 0
        self._scoped_indexes.clear()
        self._line_indexes.clear()

    def update_global(self) -> int:
        self._global_index += 1
        return self._global_index

    def update_scoped(self, scope_id: str) -> int:
        if scope_id not in self._scoped_indexes:
            self._scoped_indexes[scope_id] = 0
        self._scoped_indexes[scope_id] += 1
        return self._scoped_indexes[scope_id]

    def get_scoped(self, scope_id: str) -> int:
        return self._scoped_indexes.get(scope_id, 0)

    def update_line(self, line_key: str) -> int:
        if line_key not in self._line_indexes:
            self._line_indexes[line_key] = 0
        self._line_indexes[line_key] += 1
        return self._line_indexes[line_key]

    def get_line(self, line_key: str) -> int:
        return self._line_indexes.get(line_key, 0)

    def push_scope(self, scope_id: str) -> None:
        self._scope_stack.append(scope_id)

    def pop_scope(self) -> None:
        if self._scope_stack:
            self._scope_stack.pop()

    def get_current_scope(self) -> Optional[str]:
        return self._scope_stack[-1] if self._scope_stack else None


counter = Counter()


@contextmanager
def scope(name: Optional[str] = None):
    if name is None:
        name = str(uuid.uuid4())[:8]
    counter.push_scope(name)
    try:
        yield name
    finally:
        counter.pop_scope()


def get_current_scope() -> Optional[str]:
    return counter.get_current_scope()
