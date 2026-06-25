import typing as tp
from functools import partial

from .console import console
from .console import dprint  # noqa
from .format import extract_markup_from_arguments
from .format import format_list
from .frame import FrameInfo


def show(
    *args,
    markup: tp.Optional[str] = None,
    _frame: tp.Optional[FrameInfo] = None,
) -> None:
    result = format_list(
        *args, markup=markup, _frame=_frame, _elevate_parent_level=1
    )
    # dprint(args, result)
    console.print(''.join(p.render(color_code_scheme='ansi') for p in result))


def _show_alias(
    _verbosity: str, *args, markup: tp.Optional[str] = None
) -> None:
    if markup is None:
        args, markpos, markup = extract_markup_from_arguments(args)
        markup = _verbosity + markup.lstrip(':')
    else:
        markpos, markup = 0, _verbosity + markup.lstrip(':')
    result = format_list(
        *args, markup=markup, _elevate_parent_level=1, _mark_position=markpos
    )
    console.print(''.join(p.render(color_code_scheme='ansi') for p in result))


# shorthand
debug = partial(_show_alias, ':v1')
info = partial(_show_alias, ':v2')
success = partial(_show_alias, ':v4')
warning = partial(_show_alias, ':v6')
error = partial(_show_alias, ':v8')

divider = partial(_show_alias, ':d1')
exception = partial(_show_alias, ':e2')
expand = partial(_show_alias, ':l1')
expand2 = partial(_show_alias, ':l2')
index = partial(_show_alias, ':i2')
vshow = partial(_show_alias, ':n1')
