import sys
import typing as tp
from inspect import currentframe

from . import text_object as to
from .config import config
from .console import dprint  # noqa
from .frame import FrameInfo
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
    _frame: tp.Optional[FrameInfo] = None,
    _mark_position: int = 0,
) -> tp.List[to.TextObject]:
    """
    frame relationship:
        illustration:
            # 1. example.py (an external module out of neoprint)
            import neoprint as np
            def foo():
                bar()
            def bar():
                np.show('hello')
                np.show('world', ':p')

            # 2. neoprint/show.py
            def show(...):
                x = format_list(..., _elevate_parent_level=1)
                ...

            # 3. neoprint/format.py
            def format_list(...):
                ...

        this_frame: points to `format_list(...)`.
        foreign_frame: points to `bar(...)`.
        target_frame: points to `bar(...)` if ':p' is not used. ('hello'-case)
        target_frame: points to `foo(...)` if ':p' is used. ('world'-case)
    """
    if _frame is None:
        this_frame = FrameInfo(currentframe())  # type: ignore
        foreign_frame = this_frame.get_parent(1 + _elevate_parent_level)
    else:
        foreign_frame = _frame
    target_frame = foreign_frame  # to be determined later.

    if markup is None:
        args, markpos, markup = extract_markup_from_arguments(args)
    else:
        markpos = _mark_position
    # dprint(args, markup, args[-1], markup_analyzer.is_valid_markup(args[-1]))
    marks = markup_analyzer.analyze(markup, foreign_frame)

    if marks['p']:
        target_frame = foreign_frame.get_parent(marks['p'])
        assert target_frame

    # --------------------------------------------------------------------------

    result = []

    head_parts = get_head_parts(target_frame)
    result.extend(head_parts)

    # --------------------------------------------------------------------------

    before_body_parts = []

    if marks['i']:
        before_body_parts.append(to.Index(marks['i']))
        before_body_parts.append(to.Space())

    # --------------------------------------------------------------------------

    body_parts = []

    if marks['e']:
        if marks['e'] == Mark.SIMPLE_ERROR_LINE:
            for i, arg in enumerate(args or (sys.exc_info()[1],)):
                if i > 0:
                    body_parts.append(to.InBodySeparator())
                    body_parts.append(to.Space())
                if isinstance(arg, BaseException):
                    body_parts.append(to.ExceptionLine(arg))
                else:
                    body_parts.append(to.Text(arg))
                body_parts.append(to.InBodySeparator())
                body_parts.append(to.Space())
        else:
            before_body_parts.append(to.LineBreak())
            if args:
                is_exception_in_args = any(
                    isinstance(arg, BaseException) for arg in args
                )
                for i, arg in enumerate(args):
                    if i > 0:
                        body_parts.append(to.InBodySeparator())
                        body_parts.append(
                            to.LineBreak()
                            if is_exception_in_args
                            else to.Space()
                        )
                    if is_exception_in_args:
                        if isinstance(arg, BaseException):
                            body_parts.append(
                                to.ExceptionPanel(
                                    arg,
                                    show_locals=marks['e']
                                    == Mark.TRACEBACK_EXCEPTION_WITH_LOCALS,
                                )
                            )
                        else:
                            body_parts.append(to.Text(arg))
                    else:
                        body_parts.append(to.Text(arg))
            else:
                body_parts.append(to.ExceptionPanel.from_sys_exc())
        args = ()

    if marks['n']:
        varnames = foreign_frame.varnames
        if markpos:
            varnames = varnames[1:] if markpos == 1 else varnames[:-1]
        # assert len(varnames) == len(args), (varnames, args)
        if len(varnames) != len(args):
            # this may because user has modified the source code after call.
            # we should refresh the AST to get new varnames.
            foreign_frame.refresh()
            varnames = foreign_frame.varnames
            assert len(varnames) == len(args), (varnames, args)
    else:
        varnames = (None,) * len(args)

    for i, name, arg in zip(range(len(args)), varnames, args):
        if i > 0:
            body_parts.append(to.InBodySeparator())
            body_parts.append(to.Space())
        if name is None:
            body_parts.append(to.Text(arg))
        else:
            body_parts.append(to.NamedVariable(name, arg))

    if marks['r'] == Mark.RICH_FORMAT:
        body_parts = [
            to.BBCodeText(str(x)) if isinstance(x, to.Text) else x
            for x in body_parts
        ]
    elif marks['r'] == Mark.RICH_OBJECT:
        ...

    if marks['l']:
        # there are three cases:
        #   l1 and r*: expand object
        #   l2 or r2: special expand object
        #   l0 and r1: bbcode object
        if marks['l'] == Mark.EXPAND_FORMAT:
            body_parts = [
                to.ExpandedObject(x)
                if to.ExpandedObject.check_expandable(x)
                else x
                for x in body_parts
            ]
        elif (
            marks['l'] == Mark.SPECIAL_EXPAND_FORMAT
            or marks['r'] == Mark.RICH_OBJECT
        ):
            body_parts = [
                to.SpecialExpandedObject(x)
                if to.SpecialExpandedObject.check_expandable(x)
                else to.ExpandedObject(x)
                if to.ExpandedObject.check_expandable(x)
                else x
                for x in body_parts
            ]
        else:
            raise Exception('unreachable case')
        body_parts = [
            to.ExpandedObjectGroup(body_parts, head_parts + before_body_parts)
        ]

    if marks['d']:
        body_parts = [
            to.DividerLine(
                body_parts,
                head_parts + before_body_parts,
                bold=marks['d'] == Mark.THICK_DIVIDER_LINE,
            )
        ]

    if marks['v'] != Mark.NORMAL:
        global_color, global_style = marks['v']
        for part in body_parts:
            if part.editable:
                # dprint(part, global_color, global_style)
                part.color = global_color
                part.style = global_style

    result.extend(before_body_parts)
    result.extend(body_parts)

    return result


def format(*args, markup: tp.Optional[str] = None) -> str:
    if markup is None:
        args, markpos, markup = extract_markup_from_arguments(args)
    else:
        markpos, markup = 0, markup
    result = format_list(
        *args, markup=markup, _elevate_parent_level=1, _mark_position=markpos
    )
    return ''.join(p.render(color_code_scheme='none') for p in result)


# ------------------------------------------------------------------------------


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


def get_head_parts(frame: FrameInfo) -> tp.List[to.TextObject]:
    out = []
    if config.show_source:
        out.append(to.Source(frame))
    if config.show_funcname:
        if out:
            out.append(to.Space())
            out.append(to.FuncnameSeparator())
            out.append(to.Space())
        out.append(...)  # TODO
    if out:
        out.append(to.Space())
        out.append(to.BodySeparator())
        out.append(to.Space())
    return out
