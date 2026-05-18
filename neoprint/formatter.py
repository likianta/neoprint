import re
import time
from typing import Any, List, Optional, Tuple

from .console import AnsiColor, AnsiStyle, color_text
from .console import LEVEL_COLORS as COLOR_MAP
from .frame_info import FrameInfo
from .markup import ParsedMarks


class MessageFormatter:
    SEPARATOR = '  >  '
    SOURCE_COLOR = AnsiColor.BLUE
    FUNC_COLOR = AnsiColor.GREEN
    INDEX_COLOR = AnsiColor.WHITE
    DIM_COLOR = AnsiColor.WHITE

    def format_message(
        self,
        args: Tuple[Any, ...],
        frame: Optional[FrameInfo] = None,
        marks: Optional['ParsedMarks'] = None,
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

        index_part = ''
        if show_index and index_value is not None:
            index_part = color_text(f'[{index_value}]', self.INDEX_COLOR)
            parts.append(index_part)

        body_parts: List[str] = []
        if show_varnames and frame:
            varnames = frame.varnames
            if varnames and len(varnames) == len(args):
                for name, value in zip(varnames, args):
                    body_parts.append(f'{name} = {value}')
            else:
                body_parts.extend(str(a) for a in args)
        else:
            body_parts = [str(a) for a in args]

        color = COLOR_MAP.get(color_level, AnsiColor.DEFAULT)
        style = AnsiStyle.RESET
        if color_level in (3, 5, 7):
            style = AnsiStyle.DIM
        elif color_level in (4, 6, 8):
            style = AnsiStyle.BOLD

        formatted_body = self.SEPARATOR.join(body_parts)
        if color_level > 0:
            formatted_body = color_text(formatted_body, color, style)

        if parts:
            separator = color_text('  >  ', AnsiColor.WHITE)
            return separator.join(parts) + separator + formatted_body
        else:
            return formatted_body

    def format_source(self, frame: FrameInfo) -> str:
        text = f'{frame.filename}:{frame.lineno}'
        return color_text(text, self.SOURCE_COLOR, AnsiStyle.BOLD)

    def format_funcname(self, frame: FrameInfo) -> str:
        funcname = frame.funcname
        if not funcname.startswith('<'):
            funcname = f'{funcname}()'
        return color_text(funcname, self.FUNC_COLOR)

    def format_index(self, value: int, color: str = None) -> str:
        text = f'[{value}]'
        return color_text(text, color or self.INDEX_COLOR)

    def format_time(self, start: float, end: float = None) -> str:
        start_str = time.strftime('%H:%M:%S', time.localtime(start))
        if end is None:
            return color_text(f'[{start_str}]', AnsiColor.GREEN)

        diff = end - start
        color = AnsiColor.GREEN
        if diff >= 5.0:
            color = AnsiColor.RED
        elif diff >= 1.0:
            color = AnsiColor.YELLOW

        end_str = time.strftime('%H:%M:%S', time.localtime(end))
        if diff < 1.0:
            diff_str = f'{diff * 1000:.0f}ms'
        else:
            diff_str = f'{diff:.1f}s'

        return (
            f'{color_text(f"[{start_str}]", AnsiColor.GREEN)} '
            f'{color_text("->", AnsiColor.WHITE)} '
            f'{color_text(f"[{end_str}]", color)} '
            f'{color_text(f"({diff_str})", color)}'
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
        text = re.sub(r'\[(\w+)\](.+?)\[/(\w+)\]', self._rich_tag_handler, text)
        return text

    @staticmethod
    def _rich_tag_handler(m) -> str:
        color = m.group(1)
        content = m.group(2)
        closing = m.group(3)
        style = AnsiStyle.BOLD if closing == 'b' else AnsiStyle.RESET
        return color_text(content, color, style)


formatter = MessageFormatter()
