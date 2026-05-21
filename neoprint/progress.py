import typing as t
import os
from typing import Optional, Literal

from .console import debugger, get_console_width, print, AnsiColor, AnsiStyle, color_text
from .format import format
from .frame_info import from_frame, get_caller_frame
from .config import config
from .util import strip_ansi
from .markup import MarkupParser, ParsedMarks


class Progress:
    _SPINNER_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    _BAR_LENGTH = 40
    _MARKUP_PARSER = MarkupParser()
    _debug_filled_char = '█'
    _debug_empty_chars = '▁'
    _filled_char = '─'
    _empty_chars = '─'

    def __init__(
        self,
        total: t.Optional[int] = None,
        indicator_style: Literal[
            'counter', 'digital', 'decimal', 'none'
        ] = 'counter',
        bar_char: t.Optional[str] = None,
    ) -> None:
        self._total = total
        self.index = 0
        self.indicator_style = indicator_style
        self._type_determined = False
        self._is_spinner = False
        self._spinner_index = 0
        self._custom_bar_char = None
        if bar_char is not None:
            assert len(bar_char) == 1
            self._custom_bar_char = bar_char

    @property
    def total(self) -> t.Optional[int]:
        return self._total

    @total.setter
    def total(self, value: t.Optional[int]) -> None:
        if self._type_determined:
            raise ValueError(
                "Cannot set total after update() has been called "
                "and progress type has been determined."
            )
        self._total = value

    def _get_color_from_verbosity(self, verbosity: Optional[int]) -> t.Tuple[str, t.Optional[str]]:
        if verbosity is None:
            return ('', None)
        verbosity_to_color = {
            0: ('', None),
            1: (AnsiColor.BRIGHT_BLACK, None),
            2: (AnsiColor.CYAN, None),
            3: (AnsiColor.GREEN, None),
            4: (AnsiColor.BRIGHT_GREEN, None),
            5: (AnsiColor.YELLOW, None),
            6: (AnsiColor.BRIGHT_YELLOW, None),
            7: (AnsiColor.RED, None),
            8: (AnsiColor.BRIGHT_RED, AnsiStyle.BOLD),
            9: (AnsiColor.BRIGHT_WHITE, AnsiStyle.BOLD),
        }
        return verbosity_to_color.get(verbosity, ('', None))

    def _render_bar(self, bar_color: str) -> str:
        if self._is_spinner:
            if bar_color:
                return color_text(self._SPINNER_CHARS[self._spinner_index % len(self._SPINNER_CHARS)], bar_color)
            return self._SPINNER_CHARS[self._spinner_index % len(self._SPINNER_CHARS)]
        
        if self._total is None:
            return ""
        
        if self._custom_bar_char is not None:
            filled_char = self._custom_bar_char
            empty_chars = self._custom_bar_char
        elif debugger.enabled:
            filled_char = self._debug_filled_char
            empty_chars = self._debug_empty_chars
        else:
            filled_char = self._filled_char
            empty_chars = self._empty_chars
        
        progress = min(self.index, self._total) / self._total
        filled = int(progress * self._BAR_LENGTH)
        filled_chars = filled_char * filled
        empty_chars_str = empty_chars * (self._BAR_LENGTH - filled)
        
        if bar_color:
            result = color_text(filled_chars, bar_color)
            if empty_chars_str:
                result += color_text(empty_chars_str, AnsiColor.BRIGHT_BLACK)
            return result
        
        return filled_chars + empty_chars_str

    def _render_indicator(self, bar_color: str) -> str:
        if self._is_spinner:
            return ""
        
        if self._total is None:
            return ""
        
        if self.indicator_style == 'none':
            return ""
        
        progress = min(self.index, self._total) / self._total
        
        if self.indicator_style == 'counter':
            total_len = len(str(self._total))
            current = str(self.index).rjust(total_len)
            indicator_str = f"[{current}/{self._total}]"
        elif self.indicator_style == 'digital':
            percentage = int(progress * 100)
            indicator_str = f"[{percentage:>3}%]"
        elif self.indicator_style == 'decimal':
            percentage = progress * 100
            indicator_str = f"[{percentage:>6.2f}%]"
        else:
            indicator_str = ""
        
        if bar_color:
            return color_text(indicator_str, bar_color) + " "
        return indicator_str + " "

    def _render(self, args: t.Tuple, marks: ParsedMarks) -> str:
        extra_levels = marks.parent if marks.parent is not None else 0
        frame = get_caller_frame(extra_levels=1 + extra_levels)
        caller_info = ""
        if frame and config.show_source:
            filename = os.path.basename(frame.filepath)
            lineno = frame.lineno
            filename_part = color_text(filename, AnsiColor.BLUE, AnsiStyle.BOLD)
            colon_part = color_text(':', AnsiColor.BLUE, AnsiStyle.DIM)
            lineno_part = color_text(f'{lineno:<3}', AnsiColor.BLUE, AnsiStyle.DIM)
            caller_info = filename_part + colon_part + lineno_part
        
        # Progress bar and indicator always red by default
        bar_color = AnsiColor.RED
        bar = self._render_bar(bar_color)
        indicator = self._render_indicator(bar_color)
        
        body_parts = []
        if args:
            if marks.verbosity is not None:  # only color text if we have explicit verbosity
                text_color, text_style = self._get_color_from_verbosity(marks.verbosity)
                for arg in args:
                    if text_color:
                        body_parts.append(color_text(str(arg), text_color, text_style))
                    else:
                        body_parts.append(str(arg))
            else:  # no explicit verbosity, text is plain
                for arg in args:
                    body_parts.append(str(arg))
        
        line_content = ""
        if caller_info:
            line_content += caller_info + " " + color_text('|', AnsiColor.BRIGHT_BLACK) + " "
        line_content += bar + " " + indicator
        if body_parts:
            separator = color_text(';', AnsiColor.BRIGHT_BLACK) + " "
            line_content += separator.join(body_parts)
        
        if not debugger.enabled:
            console_width = get_console_width()
            stripped_length = len(strip_ansi(line_content))
            if stripped_length > console_width:
                excess = stripped_length - console_width + 3
                line_content = line_content[:-excess] + "..."
        
        return line_content

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        if not self._type_determined:
            self._type_determined = True
            self._is_spinner = self._total is None
        
        self.index += 1
        if self._is_spinner:
            self._spinner_index += 1
        
        # Parse markup, same logic as show()
        markup_str = kwargs.pop('markup', '')
        
        if args and isinstance(args[0], str) and args[0].startswith(':'):
            markup_str = args[0]
            args = args[1:]
        elif (
            args
            and isinstance(args[-1], str)
            and args[-1].startswith(':')
            and self._MARKUP_PARSER.is_valid_markup(args[-1])
        ):
            markup_str = args[-1]
            args = args[:-1]
        
        marks = self._MARKUP_PARSER.parse(markup_str) if markup_str else ParsedMarks()
        
        line = self._render(args, marks)
        
        end = '\n' if debugger.enabled else '\033[K\r'
        print(line, end=end, flush=True)

    def __enter__(self) -> 'Progress':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not debugger.enabled:
            print()  # 添加换行，确保进度条后有新的一行
