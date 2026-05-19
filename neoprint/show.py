import traceback
from inspect import currentframe
from typing import Any

from . import console
from .config import config
from .console import color_text, LEVEL_COLORS, AnsiStyle
from .formatter import formatter
from .frame_info import FrameInfo, from_frame
from .markup import MarkupParser, ParsedMarks
from .format import format
from .scope import counter


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


def show(*args: Any, **kwargs: Any) -> None:
    extra_levels = kwargs.pop('_extra_levels', 0)
    markup_str = kwargs.pop('markup', '')

    if args and isinstance(args[0], str) and args[0].startswith(':'):
        markup_str = args[0]
        args = args[1:]
    elif (
        args
        and isinstance(args[-1], str)
        and args[-1].startswith(':')
        and _parser.is_valid_markup(args[-1])
    ):
        markup_str = args[-1]
        args = args[:-1]

    marks = _parser.parse(markup_str) if markup_str else ParsedMarks()

    if marks.parent is not None and marks.parent > 0:
        frame = _get_caller_frame(extra_levels + marks.parent)
    else:
        frame = _get_caller_frame(extra_levels)

    color_level = marks.verbosity if marks.verbosity is not None else 0

    if marks.divider is not None:
        from .console import get_console_width

        width = get_console_width() - 4
        divider = formatter.format_divider('-', width)
        console.print(divider)

    if marks.show_varnames is not None and marks.show_varnames > 0 and args:
        from .sourcemap import get_varnames_from_call

        varnames = get_varnames_from_call(
            frame.filepath, frame.lineno, 'np.show'
        )
        if not varnames:
            varnames = get_varnames_from_call(
                frame.filepath, frame.lineno, 'show'
            )
        frame.varnames = varnames if varnames else ()

    if not args:
        return

    exception_args = [arg for arg in args if isinstance(arg, BaseException)]
    if exception_args and color_level > 0:
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

        if marks.expand is not None:
            for exc in exception_args:
                tb_lines = traceback.format_exception(
                    type(exc), exc, exc.__traceback__
                )
                indented_lines = []
                for line in tb_lines:
                    stripped = line.rstrip('\n')
                    if stripped:
                        if stripped.startswith('Traceback'):
                            indented_lines.append('    ' + stripped)
                        elif stripped.startswith('  File'):
                            file_part, rest = (
                                stripped.split('\n', 1)
                                if '\n' in stripped
                                else (stripped, '')
                            )
                            indented_lines.append('        ' + file_part[2:])
                            if rest:
                                for subline in rest.split('\n'):
                                    if subline.strip():
                                        indented_lines.append(
                                            '            ' + subline.strip()
                                        )
                        elif stripped.startswith('ZeroDivisionError'):
                            indented_lines.append('    ' + stripped)
                        else:
                            indented_lines.append('    ' + stripped)
                    else:
                        indented_lines.append('')
                indented_tb = '\n'.join(indented_lines)

                if parts:
                    prefix = head_sep_2.join(parts) + '  | '
                    full_output = '\n' + prefix + '\n' + indented_tb + '\n'
                else:
                    full_output = indented_tb

                console.print(full_output)
        else:
            for exc in exception_args:
                exc_str = str(exc)

                if parts:
                    prefix = head_sep_2.join(parts) + '  | '
                    full_output = prefix + exc_str
                else:
                    full_output = exc_str

                console.print(full_output)
    else:
        output = format(
            *args,
            markup=markup_str,
            color_code_scheme='ansi',
            _caller_filepath=frame.filepath,
            _caller_lineno=frame.lineno,
        )

        if marks.rich is not None:
            output = formatter.apply_rich_markup(output)

        console.print(output)
