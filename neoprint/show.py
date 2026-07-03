import typing as tp
from functools import partial

from .console import bprint
from .console import cprint
from .console import dprint  # noqa
from .format import E
from .format import extract_markup_from_arguments
from .format import format_list
from .frame import FrameInfo
from .text_object import LineBreak
from .text_object import Markdown


def show(
    *args,
    markup: tp.Optional[str] = None,
    _frame: tp.Optional[FrameInfo] = None,
    #   seldomly used, only for internal use. see also 
    #   `.control._variable_print`.
) -> None:
    try:
        result = format_list(
            *args,
            markup=markup,
            _frame=_frame,
            _elevate_parent_level=1,
            _raise_builtin_print=True,
        )
    except E.BuiltinPrintRequired as e:
        bprint(*e.args)
    else:
        # dprint(args, result)
        cprint(''.join(p.render(color_code_scheme='ansi') for p in result))


def _show_alias(
    _verbosity: str, *args, markup: tp.Optional[str] = None
) -> None:
    if markup is None:
        args, markpos, markup = extract_markup_from_arguments(args)
        markup = _verbosity + markup.lstrip(':')
    else:
        markpos, markup = 0, _verbosity + markup.lstrip(':')
    try:
        result = format_list(
            *args,
            markup=markup,
            _elevate_parent_level=1,
            _mark_position=markpos,
            _raise_builtin_print=True,
        )
    except E.BuiltinPrintRequired as e:
        bprint(*e.args)
    else:
        cprint(''.join(p.render(color_code_scheme='ansi') for p in result))


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


def markdown(*args: str) -> None:
    text: str
    markup: str
    if len(args) == 1:
        assert args[0][0] != ':'
        text = args[0]
        markup = ''
    elif len(args) == 2:
        if args[0][0] == ':':
            text = args[1]
            markup = args[0]
        else:
            text = args[0]
            markup = args[1]
    else:
        raise ValueError(len(args))

    text_objs = []
    text_objs.extend(format_list(markup=markup, _elevate_parent_level=1))
    text_objs.append(LineBreak())
    text_objs.append(Markdown(text))
    cprint(''.join(p.render(color_code_scheme='ansi') for p in text_objs))
