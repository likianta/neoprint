import traceback
from inspect import currentframe
from typing import Any

from . import console
from .config import config
from .console import AnsiStyle, LEVEL_COLORS
from .format import format
from .formatter import formatter
from .frame_info import FrameInfo, from_frame
from .markup import MarkupParser, ParsedMarks


def _get_caller_frame(extra_levels: int = 0) -> FrameInfo:
    frame = currentframe()
    if frame is None:
        return FrameInfo('<unknown>', 0, '<unknown>')
    levels = 2 + extra_levels
    for _ in range(levels):
        frame = frame.f_back
        if frame is None:
            return FrameInfo('<unknown>', 0, '<unknown>')
    return from_frame(frame)


_parser = MarkupParser()


def _format_rich_traceback(exc: BaseException, show_locals: bool = False) -> str:
    """Format a rich-style traceback without using rich library."""
    import os
    
    lines = []
    tb_lines = traceback.extract_tb(exc.__traceback__)
    
    # Header
    lines.append('\u250c' + '\u2500' * 76 + '\u2510')
    lines.append('\u2502 ' + '[ERROR] Traceback (most recent call last)'.ljust(75) + ' \u2502')
    lines.append('\u251c' + '\u2500' * 76 + '\u2524')
    
    # Stack frames
    for i, (filepath, lineno, funcname, source) in enumerate(reversed(tb_lines)):
        filename = os.path.basename(filepath)
        lines.append(f'\u2502 {filename}:{lineno} in {funcname}'.ljust(77) + ' \u2502')
        lines.append('\u2502'.ljust(79) + ' \u2502')
        
        if source:
            source = source.strip()
            lines.append(f'\u2502   > {source}'.ljust(77) + ' \u2502')
        lines.append('\u2502'.ljust(79) + ' \u2502')
        
        # Show locals if requested
        if show_locals:
            lines.append('\u2502   ┌── locals ──┐'.ljust(77) + ' \u2502')
            try:
                # Get locals from frame
                frame = exc.__traceback__
                for _ in range(len(tb_lines) - i - 1):
                    frame = frame.tb_next
                if frame:
                    frame_locals = frame.tb_frame.f_locals
                    max_len = 0
                    for key, value in frame_locals.items():
                        if not key.startswith('_'):
                            max_len = max(max_len, len(key))
                    
                    for key, value in frame_locals.items():
                        if not key.startswith('_'):
                            value_str = str(value)
                            if len(value_str) > 30:
                                value_str = value_str[:27] + '...'
                            lines.append(f'\u2502   │ {key.ljust(max_len)} = {value_str}'.ljust(77) + ' \u2502')
            except Exception:
                pass
            lines.append('\u2502   └──────────┘'.ljust(77) + ' \u2502')
            lines.append('\u2502'.ljust(79) + ' \u2502')
    
    # Footer with exception
    lines.append('\u251c' + '\u2500' * 76 + '\u2524')
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    lines.append(f'\u2502 {exc_type}:{exc_msg}'.ljust(77) + ' \u2502')
    lines.append('\u2514' + '\u2500' * 76 + '\u2518')
    
    return '\n'.join(lines)


def show(*args: Any, **kwargs: Any) -> None:
    extra_levels = kwargs.pop('_extra_levels', 0)
    markup_str = kwargs.pop('markup', '')
    markup_pos = 0  # 0=from kwarg, 1=from args[0], -1=from args[-1]

    if not markup_str:
        if args and isinstance(args[0], str) and args[0].startswith(':'):
            markup_str = args[0]
            args = args[1:]
            markup_pos = 1
        elif (
            args
            and isinstance(args[-1], str)
            and args[-1].startswith(':')
            and _parser.is_valid_markup(args[-1])
        ):
            markup_str = args[-1]
            args = args[:-1]
            markup_pos = -1

    marks = _parser.parse(markup_str) if markup_str else ParsedMarks()

    original_frame = _get_caller_frame(extra_levels)

    if marks.parent is not None and marks.parent > 0:
        frame = _get_caller_frame(extra_levels + marks.parent)
    else:
        frame = original_frame

    if marks.exception is not None:
        color_level = 8
        if marks.exception == 0:
            marks.long = 0
        elif marks.exception == 1:
            marks.long = 1
        elif marks.exception >= 2:
            marks.long = 2
    else:
        color_level = marks.verbosity if marks.verbosity is not None else 0

    if marks.show_varnames is not None and marks.show_varnames > 0 and args:
        from .sourcemap import get_varnames_from_call

        funcnames = [
            'np.show', 'show',
            'np.print', 'print',
            'np.debug', 'debug',
            'np.info', 'info',
            'np.success', 'success',
            'np.warning', 'warning',
            'np.error', 'error',
        ]
        
        varnames = ()
        for funcname in funcnames:
            varnames = get_varnames_from_call(
                original_frame.filepath, original_frame.lineno, funcname
            )
            if varnames:
                break
        
        if varnames and markup_pos != 0:
            varnames_list = list(varnames)
            if markup_pos == 1:
                varnames_list.pop(0)
            elif markup_pos == -1:
                varnames_list.pop(-1)
            varnames = tuple(varnames_list)

        frame.varnames = varnames if varnames else ()

    if not args:
        if marks.index is not None or (marks.divider is not None and marks.divider > 0):
            output = format(
                markup=markup_str,
                color_code_scheme='ansi',
                _caller_filepath=frame.filepath,
                _caller_lineno=frame.lineno,
                _caller_funcname=frame.funcname,
            )
            if output:
                console.print(output)
        return

    exception_args = [arg for arg in args if isinstance(arg, BaseException)]
    if exception_args and color_level > 0:
        long_level = marks.long if marks.long is not None else 0
        
        if long_level >= 1:
            show_locals = long_level >= 2
            for exc in exception_args:
                formatted_tb = _format_rich_traceback(exc, show_locals=show_locals)
                console.print(formatted_tb)
        else:
            color = LEVEL_COLORS.get(color_level, '')
            style = AnsiStyle.BOLD if color_level in (4, 6, 8) else AnsiStyle.RESET

            parts: list[str] = []
            if frame and config.show_source:
                source_part = (
                    f'{frame.filename}:{formatter._pad_lineno(frame.lineno)}'
                )
                parts.append(source_part)
            if frame and config.show_funcname:
                funcname = frame.funcname
                if not funcname.startswith('<'):
                    funcname = f'{funcname}()'
                parts.append(funcname)

            head_sep_2 = ' | '

            for exc in exception_args:
                exc_str = str(exc)

                if parts:
                    prefix = head_sep_2.join(parts) + '  | '
                    full_output = prefix + exc_str
                else:
                    full_output = exc_str

                console.print(full_output)
    else:
        varnames_for_format = frame.varnames if hasattr(frame, 'varnames') else None
        output = format(
            *args,
            markup=markup_str,
            color_code_scheme='ansi',
            _caller_filepath=frame.filepath,
            _caller_lineno=frame.lineno,
            _caller_funcname=frame.funcname,
            _varnames=varnames_for_format,
        )

        if marks.rich is not None:
            output = formatter.apply_rich_markup(output)

        console.print(output)


def _combine_marks(default_mark: str, args: tuple, kwargs: dict) -> tuple:
    user_mark = ''
    
    if 'markup' in kwargs:
        user_mark = kwargs.pop('markup')
    elif args and isinstance(args[0], str) and args[0].startswith(':') and _parser.is_valid_markup(args[0]):
        user_mark = args[0]
        args = args[1:]
    elif args and isinstance(args[-1], str) and args[-1].startswith(':') and _parser.is_valid_markup(args[-1]):
        user_mark = args[-1]
        args = args[:-1]
    
    combined_mark = default_mark + user_mark
    kwargs['markup'] = combined_mark
    return args, kwargs


def print(*args: Any, **kwargs: Any) -> None:
    args, kwargs = _combine_marks('', args, kwargs)
    show(*args, _extra_levels=1, **kwargs)


def debug(*args: Any, **kwargs: Any) -> None:
    args, kwargs = _combine_marks(':v1', args, kwargs)
    show(*args, _extra_levels=1, **kwargs)


def info(*args: Any, **kwargs: Any) -> None:
    args, kwargs = _combine_marks(':v2', args, kwargs)
    show(*args, _extra_levels=1, **kwargs)


def success(*args: Any, **kwargs: Any) -> None:
    args, kwargs = _combine_marks(':v4', args, kwargs)
    show(*args, _extra_levels=1, **kwargs)


def warning(*args: Any, **kwargs: Any) -> None:
    args, kwargs = _combine_marks(':v6', args, kwargs)
    show(*args, _extra_levels=1, **kwargs)


def error(*args: Any, **kwargs: Any) -> None:
    args, kwargs = _combine_marks(':v8', args, kwargs)
    show(*args, _extra_levels=1, **kwargs)


__all__ = ['show', 'print', 'debug', 'info', 'success', 'warning', 'error']
