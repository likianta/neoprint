import builtins
import typing as tp
from contextlib import contextmanager

from .config import internal_state
from .console import bprint
from .console import dprint
from .frame import get_last_frame
from .show import show

_effected_packages: tp.Set[str] = {'__main__'}


@contextmanager
def elevate_parent_level() -> tp.Generator:
    internal_state['parent_level'] += 1
    try:
        yield
    finally:
        internal_state['parent_level'] -= 1
        # assert internal_state['parent_level'] >= 0


def setup(package_name: tp.Optional[str] = None) -> None:
    """
    Usage:
        foo/__init__.py
            import neoprint as np
            np.setup(__package__)
    """
    if package_name:
        # NOTE: we collect only the top-level names.
        package_name = package_name.split('.')[0]
    else:
        package_name = get_last_frame().package_name
        if not package_name:
            show(
                'cannot setup neoprint: no package name found, are you in '
                '<string> evaluation?',
                ':pv8',
            )
            return

    dprint('watch prints to package', package_name)
    _effected_packages.add(package_name)
    if getattr(builtins, 'print') is bprint:
        setattr(builtins, 'print', _variable_print)


def unload() -> None:
    if getattr(builtins, 'print') is not bprint:
        setattr(builtins, 'print', bprint)


def _variable_print(*args, **kwargs) -> None:
    frame = get_last_frame(1 + internal_state['parent_level'])
    dprint(
        'variable print',
        '{} ({})'.format(
            frame.package_name,
            'hit' if frame.package_name in _effected_packages else 'miss',
        ),
        frame.file_path,
        frame.line_number,
    )
    if frame.package_name in _effected_packages:
        show(*args, _frame=frame, **kwargs)
    else:
        bprint(*args, **kwargs)
