import re
import time
from typing import Any, List, Optional, Tuple

from .console import AnsiColor, AnsiStyle, color_text
from .console import LEVEL_COLORS as COLOR_MAP
from .frame_info import FrameInfo
from .markup import MarkupParser, ParsedMarks


class MessageFormatter:
    SEPARATOR = '  >  '
    SOURCE_COLOR = AnsiColor.BLUE
    FUNC_COLOR = AnsiColor.GREEN
    INDEX_COLOR = AnsiColor.WHITE
    DIM_COLOR = AnsiColor.WHITE

    _ansi_to_bbcode = {
        AnsiColor.BLACK: 'black',
        AnsiColor.RED: 'red',
        AnsiColor.GREEN: 'green',
        AnsiColor.YELLOW: 'yellow',
        AnsiColor.BLUE: 'blue',
        AnsiColor.MAGENTA: 'magenta',
        AnsiColor.CYAN: 'cyan',
        AnsiColor.WHITE: 'white',
        AnsiColor.BRIGHT_BLACK: 'bright_black',
        AnsiColor.BRIGHT_RED: 'red',
        AnsiColor.BRIGHT_GREEN: 'green',
        AnsiColor.BRIGHT_YELLOW: 'yellow',
        AnsiColor.BRIGHT_BLUE: 'blue',
        AnsiColor.BRIGHT_MAGENTA: 'magenta',
        AnsiColor.BRIGHT_CYAN: 'cyan',
        AnsiColor.BRIGHT_WHITE: 'white',
    }

    def _format_value(self, value: Any) -> str:
        if isinstance(value, str):
            return '"{}"'.format(value)
        return str(value)

    def _color_text_none(self, text: str, color: str = None, style: str = '') -> str:
        return text

    def _color_text_bbcode(self, text: str, color: str = None, style: str = '') -> str:
        if color is None:
            return text
        bbcode_color = self._ansi_to_bbcode.get(color, 'white')
        return f'[{bbcode_color}]{text}[/]'

    def format_message(
        self,
        args: Tuple[Any, ...],
        frame: Optional[FrameInfo],
        marks: ParsedMarks,
        show_source: bool = True,
        show_funcname: bool = True,
        show_varnames: bool = False,
        show_index: bool = False,
        color_level: int = 0,
        index_value: Optional[int] = None,
    ) -> str:
        parts: List[str] = []

        if frame and show_source:
            source_part = self.format_source(frame)
            parts.append(source_part)

        if frame and show_funcname:
            func_part = self.format_funcname(frame)
            parts.append(func_part)

        body_parts: List[str] = []

        if show_varnames and frame:
            varnames = frame.varnames
            varname_count = len(varnames)
            if varname_count > 0 and varname_count < len(args):
                prefix_args = args[:-varname_count]
                suffix_args = args[-varname_count:]
                body_parts = [str(a) for a in prefix_args]
                for arg, varname in zip(suffix_args, varnames):
                    body_parts.append('{} = {}'.format(
                        varname, self._format_value(arg)
                    ))
            elif varname_count > 0:
                for arg, varname in zip(args, varnames):
                    body_parts.append('{} = {}'.format(
                        varname, self._format_value(arg)
                    ))
            else:
                body_parts = [self._format_value(a) for a in args]
        else:
            body_parts = [self._format_value(a) for a in args]

        if show_index and index_value is not None:
            index_part = color_text(
                '[{}]'.format(index_value), self.INDEX_COLOR
            )
            body_parts.insert(0, index_part)

        color = COLOR_MAP.get(color_level, AnsiColor.DEFAULT)
        style = AnsiStyle.RESET
        if color_level in (3, 5, 7):
            style = AnsiStyle.DIM
        elif color_level in (4, 6, 8):
            style = AnsiStyle.BOLD

        separator = color_text('; ', AnsiColor.BRIGHT_BLACK)
        formatted_body = separator.join(body_parts)
        if color_level > 0:
            formatted_body = color_text(formatted_body, color, style)

        if parts:
            head_sep = color_text('  >  ', AnsiColor.WHITE)
            return head_sep.join(parts) + head_sep + formatted_body
        else:
            return formatted_body

    def format_source(self, frame: FrameInfo) -> str:
        text = '{}:{}'.format(frame.filename, frame.lineno)
        return color_text(text, self.SOURCE_COLOR, AnsiStyle.BOLD)

    def format_funcname(self, frame: FrameInfo) -> str:
        funcname = frame.funcname
        if not funcname.startswith('<'):
            funcname = '{}{}'.format(funcname, '()')
        return color_text(funcname, self.FUNC_COLOR)

    def format_index(self, value: int, color: str = None) -> str:
        text = '[{}]'.format(value)
        return color_text(text, color or self.INDEX_COLOR)

    def format_time(self, start: float, end: float = None) -> str:
        start_str = time.strftime('%H:%M:%S', time.localtime(start))
        if end is None:
            return color_text('[{}]'.format(start_str), AnsiColor.GREEN)

        diff = end - start
        color = AnsiColor.GREEN
        if diff >= 5.0:
            color = AnsiColor.RED
        elif diff >= 1.0:
            color = AnsiColor.YELLOW

        end_str = time.strftime('%H:%M:%S', time.localtime(end))
        if diff < 1.0:
            diff_str = '{:.0f}ms'.format(diff * 1000)
        else:
            diff_str = '{:.1f}s'.format(diff)

        return '{s_start} {arrow} {s_end} {s_diff}'.format(
            s_start=color_text('[{}]'.format(start_str), AnsiColor.GREEN),
            arrow=color_text('->', AnsiColor.WHITE),
            s_end=color_text('[{}]'.format(end_str), color),
            s_diff=color_text('({})'.format(diff_str), color),
        )

    def format_divider(self, pattern: str = '-', width: int = 60) -> str:
        line = pattern * width
        return color_text(line, AnsiColor.YELLOW)

    def apply_rich_markup(self, text: str) -> str:
        text = re.sub(
            r'\[(\w+)\](.+?)\[/\]',
            lambda m: color_text(m.group(2), m.group(1)),
            text,
        )
        text = re.sub(
            r'\[(\w+)\](.+?)\[/(\w+)\]',
            self._rich_tag_handler,
            text,
        )
        return text

    @staticmethod
    def _rich_tag_handler(m) -> str:
        color = m.group(1)
        content = m.group(2)
        closing = m.group(3)
        style = AnsiStyle.BOLD if closing == 'b' else AnsiStyle.RESET
        return color_text(content, color, style)

    def get_body_string(
        self,
        *args: Any,
        markup: str = '',
        _caller_filepath: str = None,
        _caller_lineno: int = None,
    ) -> str:
        from inspect import currentframe
        from .sourcemap import get_varnames_from_call

        parser = MarkupParser()
        marks = parser.parse(markup) if markup else ParsedMarks()

        if _caller_filepath and _caller_lineno:
            filepath = _caller_filepath
            lineno = _caller_lineno
        else:
            frame = currentframe()
            if frame is None:
                return ' '.join(str(a) for a in args)

            caller_frame = frame.f_back
            if caller_frame is None:
                return ' '.join(str(a) for a in args)

            filepath = caller_frame.f_code.co_filename
            lineno = caller_frame.f_lineno

        varnames = get_varnames_from_call(filepath, lineno, 'np.show')
        if not varnames:
            varnames = get_varnames_from_call(
                filepath, lineno, 'np.get_body_string'
            )
        if not varnames:
            varnames = get_varnames_from_call(filepath, lineno, 'show')
        if not varnames:
            varnames = get_varnames_from_call(
                filepath, lineno, 'get_body_string'
            )

        color_level = marks.color if marks.color is not None else 0

        body_parts: List[str] = []
        if marks.show_varnames is not None and marks.show_varnames > 0 and varnames:
            if len(varnames) == len(args):
                for name, value in zip(varnames, args):
                    body_parts.append('{} = {}'.format(
                        name, self._format_value(value)
                    ))
            else:
                body_parts.extend(self._format_value(a) for a in args)
        else:
            body_parts = [self._format_value(a) for a in args]

        color = COLOR_MAP.get(color_level, AnsiColor.DEFAULT)
        style = AnsiStyle.RESET
        if color_level in (3, 5, 7):
            style = AnsiStyle.DIM
        elif color_level in (4, 6, 8):
            style = AnsiStyle.BOLD

        separator = color_text('; ', AnsiColor.BRIGHT_BLACK)
        result = separator.join(body_parts)
        if color_level > 0:
            result = color_text(result, color, style)
        return result

    def format(
        self,
        *args: Any,
        markup: str = '',
        color_code_scheme: str = 'none',
        _caller_filepath: str = None,
        _caller_lineno: int = None,
        _index_value: int = None,
        _index: int = None,
    ) -> str:
        from inspect import currentframe
        from .sourcemap import get_varnames_from_call

        parser = MarkupParser()
        marks = parser.parse(markup) if markup else ParsedMarks()

        color_level = marks.color if marks.color is not None else 0

        color = COLOR_MAP.get(color_level, AnsiColor.DEFAULT)

        if color_code_scheme == 'none':
            color_func = self._color_text_none
        elif color_code_scheme == 'bbcode':
            color_func = self._color_text_bbcode
        else:
            color_func = color_text

        if _caller_filepath and _caller_lineno:
            filepath = _caller_filepath
            lineno = _caller_lineno
        else:
            frame = currentframe()
            if frame is not None:
                caller_frame = frame.f_back
                if caller_frame is not None:
                    filepath = caller_frame.f_code.co_filename
                    lineno = caller_frame.f_lineno
                else:
                    filepath = None
                    lineno = None
            else:
                filepath = None
                lineno = None

        body_parts: List[str] = []
        if marks.show_varnames is not None and marks.show_varnames > 0 and filepath and lineno:
            varnames = get_varnames_from_call(filepath, lineno, 'np.show')
            if not varnames:
                varnames = get_varnames_from_call(filepath, lineno, 'np.format')
            if not varnames:
                varnames = get_varnames_from_call(filepath, lineno, 'show')
            if not varnames:
                varnames = get_varnames_from_call(filepath, lineno, 'format')

            if varnames and len(varnames) == len(args):
                for name, value in zip(varnames, args):
                    body_parts.append('{} = {}'.format(
                        name, self._format_value(value)
                    ))
            else:
                body_parts = [self._format_value(a) for a in args]
        else:
            body_parts = [str(a) for a in args]

        if color_level > 0:
            body_parts = [color_func(part, color) for part in body_parts]

        separator = color_func('; ', AnsiColor.BRIGHT_BLACK)
        result = separator.join(body_parts)

        index_str = ''
        if _index is not None and _index_value is not None:
            index_str = color_func('[{}] '.format(_index_value), AnsiColor.WHITE)

        return index_str + result


formatter = MessageFormatter()
