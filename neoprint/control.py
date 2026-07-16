import builtins
import typing as tp
from contextlib import contextmanager

from .config import internal_state
from .console import bprint
from .frame import get_last_frame
from .show import show

_effected_packages = set()


@contextmanager
def elevate_parent_level() -> tp.Generator:
    internal_state['parent_level'] += 1
    try:
        yield
    finally:
        internal_state['parent_level'] -= 1
        # assert internal_state['parent_level'] >= 0


def setup(scope: str = 'this_package') -> None:
    assert scope == 'this_package', (
        'only "this_package" scope is supported for now',
        scope,
    )
    frame = get_last_frame()
    _effected_packages.add(frame.package_name)
    if getattr(builtins, 'print') is bprint:
        setattr(builtins, 'print', _variable_print)


def unload() -> None:
    if getattr(builtins, 'print') is not bprint:
        setattr(builtins, 'print', bprint)


def _variable_print(*args, **kwargs) -> None:
    frame = get_last_frame(1 + internal_state['parent_level'])
    if frame.package_name in _effected_packages:
        show(*args, _frame=frame, **kwargs)
    else:
        bprint(*args, **kwargs)
