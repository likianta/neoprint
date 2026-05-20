import inspect
import typing as t
from typing import Any, Optional, Literal, List

from .markup import MarkupParser, ParsedMarks
from .scope import counter
from .config import config
from .console import AnsiColor, AnsiStyle
from .console import LEVEL_COLORS as COLOR_MAP
from .text_object import (
    TextObject, FileName, LineSeparator, LineNumber,
    Funcname, BodySeparator, InBodySeparator, BodyPart,
    IndexMarker, Space
)
from .frame_info import FrameInfo


_parser = MarkupParser()


def _find_caller_frame(this_frame, parent_level: int) -> inspect.FrameInfo:
    frame = this_frame.f_back
    for _ in range(parent_level):
        if frame is not None:
            frame = frame.f_back
    return frame


def format_list(
    *args: Any,
    markup: t.Union[str, ParsedMarks] = '',
    _caller_filepath: Optional[str] = None,
    _caller_lineno: Optional[int] = None,
    _caller_funcname: Optional[str] = None,
    _index_value: Optional[int] = None,
    _index: Optional[int] = None,
    _varnames: Optional[tuple] = None,
    _extra_levels: int = 0,
    _varname_frame: Optional[inspect.FrameInfo] = None,
    _target_frame: Optional[inspect.FrameInfo] = None,
) -> List[TextObject]:
    text_objs: List[TextObject] = []

    if isinstance(markup, ParsedMarks):
        marks = markup
    else:
        if args and isinstance(args[0], str) and args[0].startswith(':'):
            markup = args[0]
            args = args[1:]
        elif args and isinstance(args[-1], str) and args[-1].startswith(':'):
            markup = args[-1]
            args = args[:-1]
        marks = _parser.parse(markup) if markup else ParsedMarks()

    frame_info = None
    
    if _target_frame is not None:
        filepath = _target_frame.f_code.co_filename
        lineno = _target_frame.f_lineno
        funcname = _target_frame.f_code.co_name
        frame_info = FrameInfo(filepath, lineno, funcname)
    elif _caller_filepath and _caller_lineno:
        filepath = _caller_filepath
        lineno = _caller_lineno
        funcname = _caller_funcname or '<module>'
        frame_info = FrameInfo(filepath, lineno, funcname)
    else:
        frame = inspect.currentframe()
        if frame is not None:
            caller_frame = frame.f_back
            for _ in range(_extra_levels):
                if caller_frame is not None:
                    caller_frame = caller_frame.f_back
            if caller_frame is not None:
                filepath = caller_frame.f_code.co_filename
                lineno = caller_frame.f_lineno
                funcname = caller_frame.f_code.co_name
                frame_info = FrameInfo(filepath, lineno, funcname)

    effective_index = _index if _index is not None else marks.index
    index_value = _index_value
    
    if index_value is None and effective_index is not None:
        if effective_index == 0:
            counter.reset_all()
            index_value = None
        elif effective_index == 1 and frame_info:
            line_key = f'{frame_info.filepath}:{frame_info.lineno}'
            index_value = counter.update_line(line_key)
        elif effective_index == 2 and frame_info:
            current_scope = counter.get_current_scope()
            if current_scope:
                scope_id = current_scope
            else:
                if _caller_funcname is not None:
                    scope_id = _caller_funcname
                else:
                    scope_id = frame_info.funcname
            index_value = counter.update_scoped(scope_id)
        elif effective_index == 3:
            index_value = counter.update_global()

    has_verbosity_mark = marks.verbosity is not None
    color_level = marks.verbosity if marks.verbosity is not None else 0
    color = COLOR_MAP.get(color_level, AnsiColor.DEFAULT)
    style = ''
    if color_level in (3, 5, 7):
        style = AnsiStyle.DIM
    elif color_level in (4, 6, 8):
        style = AnsiStyle.BOLD

    head_parts: List[TextObject] = []
    has_source_or_funcname = False

    if frame_info and config.show_source:
        has_source_or_funcname = True
        source_color = AnsiColor.RED if color_level == 9 else AnsiColor.BLUE
        filename = frame_info.filename
        head_parts.append(FileName(filename))
        head_parts.append(LineSeparator())
        head_parts.append(LineNumber(frame_info.lineno))

    if frame_info and config.show_funcname:
        has_source_or_funcname = True
        if head_parts:
            head_parts.append(Space())
        head_parts.append(Funcname(frame_info.funcname))

    if effective_index is not None and index_value is not None:
        if head_parts:
            head_parts.append(Space())
        head_parts.append(IndexMarker(index_value))

    if head_parts:
        text_objs.extend(head_parts)
        if has_source_or_funcname:
            text_objs.append(Space())
            text_objs.append(BodySeparator())
            text_objs.append(Space())
        elif effective_index is not None and index_value is not None:
            text_objs.append(Space())

    for i, arg in enumerate(args):
        if i > 0:
            text_objs.append(InBodySeparator())

        text = str(arg)
        if has_verbosity_mark and color_level > 0:
            text_objs.append(BodyPart(text, color=color, style=style))
        else:
            text_objs.append(BodyPart(text))

    return text_objs


def format(
    *args: Any,
    markup: str = '',
    color_code_scheme: str = 'none',
    _caller_filepath: Optional[str] = None,
    _caller_lineno: Optional[int] = None,
    _caller_funcname: Optional[str] = None,
    _varnames: Optional[tuple] = None,
) -> str:
    this_frame = inspect.currentframe()
    
    raw_args = args
    parsed_markup = markup
    
    if not markup:
        if args and isinstance(args[0], str) and args[0].startswith(':'):
            parsed_markup = args[0]
            raw_args = args[1:]
        elif args and isinstance(args[-1], str) and args[-1].startswith(':'):
            parsed_markup = args[-1]
            raw_args = args[:-1]
    
    marks = _parser.parse(parsed_markup) if parsed_markup else ParsedMarks()
    
    parent_level = marks.parent if marks.parent is not None else 0
    
    parent_frame = this_frame.f_back if this_frame else None
    target_frame = None
    
    if this_frame:
        target_frame = this_frame.f_back
        for _ in range(parent_level):
            if target_frame is not None:
                target_frame = target_frame.f_back

    text_objs = format_list(
        *raw_args,
        markup=marks,
        _caller_filepath=_caller_filepath,
        _caller_lineno=_caller_lineno,
        _caller_funcname=_caller_funcname,
        _varnames=_varnames,
        _varname_frame=parent_frame,
        _target_frame=target_frame,
    )

    output = ''.join(
        (t.render(color_code_scheme) for t in text_objs)
    )
    return output
