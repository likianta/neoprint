import inspect
from typing import Any, Optional

from .formatter import formatter
from .markup import MarkupParser, ParsedMarks
from .scope import counter


_parser = MarkupParser()


def format(
    *args: Any,
    markup: str = '',
    color_code_scheme: str = 'none',
    _caller_filepath: Optional[str] = None,
    _caller_lineno: Optional[int] = None,
    _caller_funcname: Optional[str] = None,
    _varnames: Optional[tuple] = None,
) -> str:
    if not markup:
        if args and isinstance(args[0], str) and args[0].startswith(':') and _parser.is_valid_markup(args[0]):
            markup = args[0]
            args = args[1:]
        elif args and isinstance(args[-1], str) and args[-1].startswith(':') and _parser.is_valid_markup(args[-1]):
            markup = args[-1]
            args = args[:-1]

    frame = inspect.currentframe()
    caller_frame = frame.f_back if frame is not None else None

    if _caller_filepath is None or _caller_lineno is None:
        caller_filepath = (
            caller_frame.f_code.co_filename
            if caller_frame is not None
            else None
        )
        caller_lineno = (
            caller_frame.f_lineno if caller_frame is not None else None
        )
    else:
        caller_filepath = _caller_filepath
        caller_lineno = _caller_lineno

    marks = _parser.parse(markup) if markup else ParsedMarks()

    index_value = None
    if marks.index is not None:
        if marks.index == 0:
            counter.reset_all()
            index_value = None
        elif marks.index == 1:
            line_key = f'{caller_filepath}:{caller_lineno}'
            index_value = counter.update_line(line_key)
        elif marks.index == 2:
            current_scope = counter.get_current_scope()
            if current_scope:
                scope_id = current_scope
            else:
                if _caller_funcname is not None:
                    scope_id = _caller_funcname
                else:
                    scope_id = (
                        caller_frame.f_code.co_name
                        if caller_frame
                        else '<module>'
                    )
            index_value = counter.update_scoped(scope_id)
        elif marks.index == 3:
            index_value = counter.update_global()

    return formatter.format(
        *args,
        markup=markup,
        color_code_scheme=color_code_scheme,
        _caller_filepath=caller_filepath,
        _caller_lineno=caller_lineno,
        _index_value=index_value,
        _index=marks.index,
        _varnames=_varnames,
    )


__all__ = ['format']
