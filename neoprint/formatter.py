import re
import time
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

from .config import config
from .console import AnsiColor, AnsiStyle, CONSOLE_WIDTH, color_text
from .console import LEVEL_COLORS as COLOR_MAP
from .frame_info import FrameInfo
from .markup import MarkupParser, ParsedMarks


class MessageFormatter:
    SOURCE_COLOR = AnsiColor.BLUE
    FUNC_COLOR = AnsiColor.GREEN
    INDEX_COLOR = AnsiColor.RED
    DIM_COLOR = AnsiColor.WHITE

    @staticmethod
    def _pad_lineno(lineno: int) -> str:
        width = 3
        while width < len(str(lineno)):
            width += 3
        return '{:<{}}'.format(lineno, width)

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

    def _color_text_none(
        self, text: str, color: Optional[str] = None, style: str = ''
    ) -> str:
        return text

    def _color_text_bbcode(
        self, text: str, color: Optional[str] = None, style: str = '', bgcolor: Optional[str] = None
    ) -> str:
        if color is None and bgcolor is None:
            return text
        
        tag_parts = []
        if style == AnsiStyle.DIM:
            tag_parts.append('dim')
        elif style == AnsiStyle.BOLD:
            tag_parts.append('bold')
        
        if color:
            bbcode_color = self._ansi_to_bbcode.get(color, 'white')
            tag_parts.append(bbcode_color)
        
        if bgcolor:
            # 处理 ANSI 背景色代码（比如 '41'）或者 AnsiColor 值
            # 映射 ANSI 背景色代码到对应的颜色
            bg_color_map = {
                '40': 'black',
                '41': 'red',
                '42': 'green',
                '43': 'yellow',
                '44': 'blue',
                '45': 'magenta',
                '46': 'cyan',
                '47': 'white',
            }
            bbcode_bgcolor = bg_color_map.get(bgcolor, 'white')
            tag_parts.append(f'on {bbcode_bgcolor}')
        
        if tag_parts:
            tag = f'[{" ".join(tag_parts)}]'
            return f'{tag}{text}[/]'
        
        return text

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
            if color_level == 9:
                filename_part = color_text(
                    frame.filename, AnsiColor.RED, AnsiStyle.BOLD
                )
                head_sep_1 = color_text(':', AnsiColor.RED, AnsiStyle.DIM)
                lineno_padded = self._pad_lineno(frame.lineno)
                lineno_part = color_text(
                    lineno_padded, AnsiColor.RED, AnsiStyle.DIM
                )
                parts.append(filename_part + head_sep_1 + lineno_part)
            else:
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
                    body_parts.append(
                        '{} = {}'.format(varname, self._format_value(arg))
                    )
            elif varname_count > 0:
                for arg, varname in zip(args, varnames):
                    body_parts.append(
                        '{} = {}'.format(varname, self._format_value(arg))
                    )
            else:
                body_parts = [self._format_value(a) for a in args]
        else:
            body_parts = [str(a) for a in args]

        if show_index and index_value is not None:
            index_part = color_text(
                '[{}]'.format(index_value), self.INDEX_COLOR
            )
            body_parts.insert(0, index_part)

        color = COLOR_MAP.get(color_level, AnsiColor.DEFAULT)
        style = AnsiStyle.RESET
        if color_level in (3, 5, 7):
            style = AnsiStyle.DIM

        # 分别给每个 body part 应用颜色
        colored_body_parts = []
        for i, part in enumerate(body_parts):
            if color_level == 9:
                colored_part = color_text(part, AnsiColor.BRIGHT_WHITE, '41')
            else:
                colored_part = (
                    color_text(part, color, style) if color_level > 0 else part
                )
            colored_body_parts.append(colored_part)

        separator = color_text(';', AnsiColor.BRIGHT_BLACK)
        formatted_body_parts = []
        for i, part in enumerate(colored_body_parts):
            if i == 0:
                formatted_body_parts.append(part)
            elif i == 1 and show_index:
                formatted_body_parts.append(' ' + part)
            else:
                formatted_body_parts.append(separator + ' ' + part)

        formatted_body = ''.join(formatted_body_parts)

        if parts:
            head_sep_2 = ' ' + color_text('|', AnsiColor.BRIGHT_BLACK) + ' '
            return ''.join(parts) + head_sep_2 + formatted_body
        else:
            return formatted_body

    def format_source(self, frame: FrameInfo) -> str:
        filename_part = color_text(
            frame.filename, self.SOURCE_COLOR, AnsiStyle.BOLD
        )
        head_sep_1 = color_text(':', self.SOURCE_COLOR, AnsiStyle.DIM)
        lineno_padded = self._pad_lineno(frame.lineno)
        lineno_part = color_text(
            lineno_padded, self.SOURCE_COLOR, AnsiStyle.DIM
        )
        return filename_part + head_sep_1 + lineno_part

    def format_funcname(self, frame: FrameInfo) -> str:
        funcname = frame.funcname
        if not funcname.startswith('<'):
            funcname = '{}{}'.format(funcname, '()')
        return color_text(funcname, self.FUNC_COLOR)

    def format_index(self, value: int, color: Optional[str] = None) -> str:
        text = '[{}]'.format(value)
        return color_text(text, color or self.INDEX_COLOR)

    def format_time(self, start: float, end: Optional[float] = None) -> str:
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

    def _format_long(self, *args: Any) -> str:
        inc = '  '

        def _fmt(obj: Any, indent: int) -> str:
            prefix = inc * indent

            if isinstance(obj, str):
                return f'"{obj}"'
            elif isinstance(obj, list):
                if not obj:
                    return f'{prefix}[]'
                items = []
                for item in obj:
                    items.append(f'{prefix}{inc}{_fmt(item, indent + 1)},')
                return f'{prefix}[\n' + '\n'.join(items) + f'\n{prefix}]'
            elif isinstance(obj, dict):
                if not obj:
                    return f'{prefix}{{}}'
                items = []
                for k, v in obj.items():
                    key_str = _fmt(k, indent + 1)
                    val_str = _fmt(v, indent + 1)
                    items.append(f'{prefix}{inc}{key_str}: {val_str},')
                return f'{prefix}{{\n' + '\n'.join(items) + f'\n{prefix}}}'
            elif isinstance(obj, tuple):
                if not obj:
                    return f'{prefix}()'
                items = []
                for item in obj:
                    items.append(f'{prefix}{inc}{_fmt(item, indent + 1)},')
                return f'{prefix}(\n' + '\n'.join(items) + f'\n{prefix})'
            elif isinstance(obj, set):
                if not obj:
                    return f'{prefix}set()'
                items = []
                for item in sorted(obj, key=str):
                    items.append(f'{prefix}{inc}{_fmt(item, indent + 1)},')
                return f'{prefix}{{\n' + '\n'.join(items) + f'\n{prefix}}}'
            elif obj is None:
                return 'None'
            elif isinstance(obj, bool):
                return 'True' if obj else 'False'
            else:
                return repr(obj)

        return '\n'.join(_fmt(arg, indent=1) for arg in args)

    def _format_long_l2(self, *args: Any) -> str:
        inc = '  '
        parts = []
        for arg in args:
            formatted = self._try_format_special(arg)
            if formatted is not None:
                parts.append(formatted)
            else:
                parts.append(self._format_long(arg))
        return '\n\n'.join(parts)

    def _try_format_special(self, obj: Any) -> Optional[str]:
        inc = '  '
        if isinstance(obj, list) and len(obj) > 0:
            if all(
                isinstance(row, (list, tuple)) and len(row) > 0
                and all(isinstance(item, str) for item in row)
                for row in obj
            ):
                table = self._format_as_table(obj)
                return '\n'.join(inc + line for line in table.splitlines())

        if isinstance(obj, dict) and len(obj) > 0:
            if all(isinstance(k, str) and isinstance(v, (str, bool, int, float)) for k, v in obj.items()):
                table = self._format_as_kv_table(obj)
                return '\n'.join(inc + line for line in table.splitlines())

        if isinstance(obj, str):
            m = re.match(r'^(.+): (.+?) -> (.+)$', obj)
            if m:
                return inc + '{}: {} -> {}'.format(
                    m.group(1),
                    color_text(m.group(2), AnsiColor.RED),
                    color_text(m.group(3), AnsiColor.GREEN),
                )
            m = re.match(r'^(.+?) -> (.+)$', obj)
            if m:
                return inc + '{} -> {}'.format(
                    color_text(m.group(1), AnsiColor.RED),
                    color_text(m.group(2), AnsiColor.GREEN),
                )

        return None

    @staticmethod
    def _format_as_table(data: Sequence[Sequence[str]]) -> str:
        col_widths = [
            max(len(str(row[i])) for row in data)
            for i in range(len(data[0]))
        ]
        lines = []
        lines.append('| ' + ' | '.join(
            str(item).ljust(w) for item, w in zip(data[0], col_widths)
        ) + ' |')
        lines.append('| ' + ' | '.join(
            '-' * w for w in col_widths
        ) + ' |')
        for row in data[1:]:
            lines.append('| ' + ' | '.join(
                str(item).ljust(w) for item, w in zip(row, col_widths)
            ) + ' |')
        return '\n'.join(lines)

    @staticmethod
    def _format_as_kv_table(data: Dict[str, Any]) -> str:
        key_width = max(len(k) for k in data.keys())
        val_width = max(len(str(v)) for v in data.values())
        lines = []
        lines.append('| ' + 'KEY'.ljust(key_width) + ' | ' + 'VALUE'.ljust(val_width) + ' |')
        lines.append('| ' + '-' * key_width + ' | ' + '-' * val_width + ' |')
        for k, v in data.items():
            lines.append('| ' + k.ljust(key_width) + ' | ' + str(v).ljust(val_width) + ' |')
        return '\n'.join(lines)

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
        _caller_filepath: Optional[str] = None,
        _caller_lineno: Optional[int] = None,
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

        color_level = marks.verbosity if marks.verbosity is not None else 0

        body_parts: List[str] = []
        if (
            marks.show_varnames is not None
            and marks.show_varnames > 0
            and varnames
        ):
            if len(varnames) == len(args):
                for name, value in zip(varnames, args):
                    body_parts.append(
                        '{} = {}'.format(name, self._format_value(value))
                    )
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
        color_code_scheme: Literal['none', 'ansi', 'bbcode'] = 'none',
        _caller_filepath: Optional[str] = None,
        _caller_lineno: Optional[int] = None,
        _index_value: Optional[int] = None,
        _index: Optional[int] = None,
        _varnames: Optional[Tuple[str, ...]] = None,
    ) -> str:
        from inspect import currentframe
        from .sourcemap import get_varnames_from_call
        from .frame_info import FrameInfo

        parser = MarkupParser()
        marks = parser.parse(markup) if markup else ParsedMarks()

        has_verbosity_mark = marks.verbosity is not None
        color_level = marks.verbosity if marks.verbosity is not None else 0

        color = COLOR_MAP.get(color_level, AnsiColor.DEFAULT)

        if color_code_scheme == 'none' or (has_verbosity_mark and color_level == 0):
            color_func = self._color_text_none
        elif color_code_scheme == 'bbcode':
            color_func = self._color_text_bbcode
        else:
            color_func = color_text

        frame_info = None
        if _caller_filepath and _caller_lineno:
            filepath = _caller_filepath
            lineno = _caller_lineno
            frame_info = FrameInfo(filepath, lineno, '<module>')
        else:
            frame = currentframe()
            if frame is not None:
                caller_frame = frame.f_back
                if caller_frame is not None:
                    filepath = caller_frame.f_code.co_filename
                    lineno = caller_frame.f_lineno
                    funcname = caller_frame.f_code.co_name
                    frame_info = FrameInfo(filepath, lineno, funcname)
                else:
                    filepath = None
                    lineno = None
            else:
                filepath = None
                lineno = None

        body_parts: List[str] = []
        if (
            marks.show_varnames is not None
            and marks.show_varnames > 0
            and filepath
            and lineno
        ):
            varnames = _varnames if _varnames else get_varnames_from_call(filepath, lineno, 'np.show')
            if not varnames:
                varnames = get_varnames_from_call(filepath, lineno, 'np.format')
            if not varnames:
                varnames = get_varnames_from_call(filepath, lineno, 'show')
            if not varnames:
                varnames = get_varnames_from_call(filepath, lineno, 'format')

            if varnames:
                body_parts = []
                for i, arg in enumerate(args):
                    if i < len(varnames) and varnames[i] is not None:
                        body_parts.append(
                            '{} = {}'.format(varnames[i], self._format_value(arg))
                        )
                    else:
                        body_parts.append(str(arg))
            else:
                body_parts = [str(a) for a in args]
        else:
            body_parts = [str(a) for a in args]

        if has_verbosity_mark and color_level > 0:
            style = AnsiStyle.DIM if color_level in (3, 5, 7) else ''
            if color_level == 9:
                if color_code_scheme == 'bbcode':
                    body_parts = [color_func(part, AnsiColor.BRIGHT_WHITE, style='', bgcolor='41') for part in body_parts]
                else:
                    body_parts = [color_func(part, AnsiColor.BRIGHT_WHITE, '41') for part in body_parts]
            elif color:
                body_parts = [color_func(part, color, style) for part in body_parts]

        # 构建新的分隔符格式
        formatted_body_parts = []
        for i, part in enumerate(body_parts):
            if i == 0:
                formatted_body_parts.append(part)
            else:
                if color_code_scheme == 'ansi' and has_verbosity_mark and color_level > 0:
                    separator = '\x1b[' + AnsiColor.BRIGHT_BLACK + 'm' + ';' + '\x1b[0m'
                else:
                    separator = color_func(';', AnsiColor.BRIGHT_BLACK)
                formatted_body_parts.append(separator + ' ' + part)
        formatted_body = ''.join(formatted_body_parts)

        # 添加 source 部分（类似于 format_message）
        parts: List[str] = []
        if frame_info and config.show_source:
            if color_level == 9:
                if color_code_scheme == 'bbcode':
                    filename_part = color_func(frame_info.filename, AnsiColor.RED, AnsiStyle.BOLD)
                    head_sep_1 = color_func(':', AnsiColor.RED, AnsiStyle.DIM)
                    lineno_padded = self._pad_lineno(frame_info.lineno)
                    lineno_part = color_func(lineno_padded, AnsiColor.RED, AnsiStyle.DIM)
                else:
                    filename_part = color_text(frame_info.filename, AnsiColor.RED, AnsiStyle.BOLD)
                    head_sep_1 = color_text(':', AnsiColor.RED, AnsiStyle.DIM)
                    lineno_padded = self._pad_lineno(frame_info.lineno)
                    lineno_part = color_text(lineno_padded, AnsiColor.RED, AnsiStyle.DIM)
                parts.append(filename_part + head_sep_1 + lineno_part)
            else:
                source_color = self.SOURCE_COLOR
                filename_part = color_func(frame_info.filename, source_color, AnsiStyle.BOLD)
                head_sep_1 = color_func(':', source_color, AnsiStyle.DIM)
                lineno_padded = self._pad_lineno(frame_info.lineno)
                lineno_part = color_func(lineno_padded, source_color, AnsiStyle.DIM)
                parts.append(filename_part + head_sep_1 + lineno_part)

        if frame_info and config.show_funcname:
            funcname = frame_info.funcname
            if not funcname.startswith('<'):
                funcname = '{}{}'.format(funcname, '()')
            func_part = color_func(funcname, self.FUNC_COLOR)
            parts.append(func_part)

        if marks.long:
            if marks.long >= 2:
                long_body = self._format_long_l2(*args)
            elif (
                marks.show_varnames is not None
                and marks.show_varnames > 0
                and filepath
                and lineno
                and varnames
            ):
                long_lines = []
                for i, arg in enumerate(args):
                    if i < len(varnames) and varnames[i] is not None:
                        vn = varnames[i]
                    else:
                        vn = None

                    arg_formatted = self._format_long(arg)
                    arg_lines = arg_formatted.splitlines()

                    if vn is not None:
                        arg_lines[0] = '  {} = {}'.format(
                            vn, arg_lines[0].lstrip()
                        )
                        if i < len(args) - 1:
                            arg_lines[-1] = arg_lines[-1] + ','

                    long_lines.extend(arg_lines)

                long_body = '\n'.join(long_lines)
            else:
                long_body = self._format_long(*args)

            if marks.long == 1 and has_verbosity_mark and color_level > 0:
                _long_style = AnsiStyle.DIM if color_level in (3, 5, 7) else ''
                _long_lines = long_body.splitlines()
                _colored_lines = []
                for _line in _long_lines:
                    _stripped = _line.lstrip()
                    _indent = _line[:len(_line) - len(_stripped)]
                    if color_level == 9:
                        if color_code_scheme == 'bbcode':
                            _colored = color_func(
                                _stripped, AnsiColor.BRIGHT_WHITE,
                                style='', bgcolor='41'
                            )
                        else:
                            _colored = color_func(
                                _stripped, AnsiColor.BRIGHT_WHITE, '41'
                            )
                    elif color:
                        _colored = color_func(_stripped, color, _long_style)
                    else:
                        _colored = _stripped
                    _colored_lines.append(_indent + _colored)
                long_body = '\n'.join(_colored_lines)

            result = long_body

            if _index is not None and _index_value is not None:
                index_str = color_func(
                    '[{}]'.format(_index_value), self.INDEX_COLOR
                )
                result = index_str + ' ' + result

            if parts:
                head_sep_2 = ' ' + color_func('|', AnsiColor.BRIGHT_BLACK) + ' '
                head_part = ''.join(parts) + head_sep_2
                _plain_result = re.sub(r'\033\[[0-9;]*m', '', result)
                _plain_lines = _plain_result.splitlines()
                if len(_plain_lines) == 1:
                    _plain_head = re.sub(r'\033\[[0-9;]*m', '', head_part)
                    if len(_plain_head) + len(_plain_lines[0].lstrip()) <= CONSOLE_WIDTH:
                        _colored_result_lines = result.splitlines()
                        result = head_part + _colored_result_lines[0].lstrip()
                    else:
                        result = head_part + '\n' + result
                else:
                    result = head_part + '\n' + result

            return result

        # Handle divider mark: wrap body with box-drawing characters
        if marks.divider:
            from .console import get_console_width

            div_char = '─'

            visible_prefix = 0
            if config.show_source and frame_info:
                visible_prefix += len(frame_info.filename) + 1 + len(self._pad_lineno(frame_info.lineno))
            if config.show_funcname and frame_info and not frame_info.funcname.startswith('<'):
                visible_prefix += len(frame_info.funcname) + 2
            if parts:
                visible_prefix += 3
            if _index is not None and _index_value is not None:
                visible_prefix += len(str(_index_value)) + 3

            total_width = get_console_width() - visible_prefix

            if color_code_scheme == 'bbcode':
                visible_body = re.sub(r'\[/?\w+(?: [^\]]+)?\]', '', formatted_body)
            elif color_code_scheme == 'ansi' and formatted_body:
                from .util import strip_ansi
                visible_body = strip_ansi(formatted_body)
            else:
                visible_body = formatted_body

            remaining = total_width - len(visible_body) - 2
            if remaining > 0:
                if remaining % 2 != 0:
                    remaining -= 1
                half = remaining // 2
            else:
                half = 0

            if formatted_body:
                if has_verbosity_mark and color_level > 0:
                    div_color = color
                    div_style = style
                    left_div = color_func(div_char * half, div_color, div_style)
                    right_div = color_func(div_char * (remaining - half), div_color, div_style)
                else:
                    left_div = div_char * half
                    right_div = div_char * (remaining - half)
                formatted_body = left_div + ' ' + formatted_body + ' ' + right_div
            else:
                if has_verbosity_mark and color_level > 0:
                    div_color = color
                    div_style = style
                else:
                    div_color = AnsiColor.BRIGHT_BLACK
                    div_style = ''
                formatted_body = color_func(div_char * total_width, div_color, div_style)

        result = formatted_body

        # 添加 index
        if _index is not None and _index_value is not None:
            index_str = color_func(
                '[{}]'.format(_index_value), self.INDEX_COLOR
            )
            result = index_str + ' ' + result

        if parts:
            head_sep_2 = ' ' + color_func('|', AnsiColor.BRIGHT_BLACK) + ' '
            result = ''.join(parts) + head_sep_2 + result

        return result


formatter = MessageFormatter()
