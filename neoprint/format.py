import typing as tp
from inspect import currentframe
from . import text_object as to
from .config import config
from .console import dprint  # noqa
from .frame_info import FrameInfo
from .markup import Mark
from .markup import markup_analyzer


class T:  # Typehint
    Args = tp.Tuple[tp.Any, ...]
    FlushScheme = int
    #   0: no flush
    #   1: instant flush
    #   2: instant flush and drain
    #   3: wait for flush
    Marks = tp.Dict[str, tp.Any]
    Markup = str
    MarkupPos = int  # -1, 0, 1


def format_list(
    *args,
    markup: tp.Optional[T.Markup] = None,
    _elevate_parent_level: int = 0,
    _mark_position: int = 0,
) -> tp.List[to.TextObject]:
    this_frame: FrameInfo = FrameInfo(currentframe())  # type: ignore
    parent_frame: FrameInfo = this_frame.get_parent(1 + _elevate_parent_level)
    caller_frame: FrameInfo = parent_frame

    if markup is None:
        args, markpos, markup = extract_markup_from_arguments(args)
    else:
        markpos = _mark_position
    # dprint(args, markup, args[-1], markup_analyzer.is_valid_markup(args[-1]))
    marks = markup_analyzer.analyze2(markup, parent_frame)
    if marks['p']:
        caller_frame = parent_frame.get_parent(marks['p'])
        assert caller_frame

    # --------------------------------------------------------------------------

    result = []

    # head part
    head_parts = []
    if config.show_source:
        head_parts.append(to.Source(caller_frame))
    if config.show_funcname:
        head_parts.append(to.Space())
        head_parts.append(to.FuncnameSeparator())
        head_parts.append(to.Space())
        ...  # TODO
    if head_parts:
        head_parts.append(to.Space())
        head_parts.append(to.BodySeparator())
        head_parts.append(to.Space())
    result.extend(head_parts)

    # --------------------------------------------------------------------------

    # body part
    body_parts = []
    if marks['i']:
        body_parts.append(to.Index(marks['i']))
        body_parts.append(to.Space())

    if marks['n']:
        varnames = parent_frame.varnames
        if markpos:
            varnames = varnames[1:] if markpos == 1 else varnames[:-1]
        assert len(varnames) == len(args), (varnames, args)
    else:
        varnames = (None,) * len(args)

    for name, arg in zip(varnames, args):
        if name is None:
            body_parts.append(to.Text(arg))
        else:
            body_parts.append(to.NamedVariable(name, arg))
        body_parts.append(to.InBodySeparator())
        body_parts.append(to.Space())
    body_parts = body_parts[:-2]

    if marks['v']:
        global_color, global_style = marks['v']
        for part in body_parts:
            if part.editable:
                part.color = global_color
                part.style = global_style

    if marks['d']:
        insertion_index = 2 if marks['i'] else 0
        a, b = body_parts[:insertion_index], body_parts[insertion_index:]
        body_parts = a + [
            to.DividerLine(
                head_parts, b, bold=marks['d'] == Mark.THICK_DIVIDER_LINE
            )
        ]

    result.extend(body_parts)

    return result


def extract_markup_from_arguments(
    args: T.Args,
) -> tp.Tuple[T.Args, int, T.Markup]:
    if (
        len(args) > 0
        and isinstance(args[0], str)
        and args[0].startswith(':')
        and markup_analyzer.is_valid_markup(args[0])
    ):
        return args[1:], 1, args[0]
    elif (
        len(args) > 1
        and isinstance(args[-1], str)
        and args[-1].startswith(':')
        and markup_analyzer.is_valid_markup(args[-1])
    ):
        return args[:-1], -1, args[-1]
    else:
        return args, 0, ''
