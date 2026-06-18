import builtins

from .console import bprint
from .frame_info import get_last_frame
from .show import show

effected_packages = set()


def setup(scope: str = 'this_package') -> None:
    assert scope == 'this_package', f'scope `{scope}` is not supported'
    frame = get_last_frame()
    effected_packages.add(frame.package_name)
    if getattr(builtins, 'print') is bprint:
        setattr(builtins, 'print', _variable_print)


def _variable_print(*args, **kwargs) -> None:
    frame = get_last_frame()
    if frame.package_name in effected_packages:
        show(*args, _frame=frame, **kwargs)
    else:
        bprint(*args, **kwargs)
