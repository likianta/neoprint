import typing as t
from typing import Optional, Literal

from . import console
from .console import AnsiColor, AnsiStyle, color_text


class TextObject:
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

    def __init__(self, data: str, color: str = '', style: str = ''):
        self._data = data
        self.color = color
        self.style = style

    @property
    def length(self) -> int:
        return len(self._data)

    def render_text(self) -> str:
        return self._data

    def render_ansi(self) -> str:
        if self.color:
            return color_text(self._data, self.color, self.style)
        return self._data

    def render_bbcode(self) -> str:
        if self.color:
            bbcode_color = self._ansi_to_bbcode.get(self.color, 'white')
            style_prefix = ''
            if self.style == AnsiStyle.BOLD:
                style_prefix = 'bold '
            elif self.style == AnsiStyle.DIM:
                style_prefix = 'dim '
            return f'[{style_prefix}{bbcode_color}]{self._data}[/]'
        return self._data

    def render(self, color_scheme: Literal['none', 'ansi', 'bbcode'] = 'none') -> str:
        if color_scheme == 'ansi':
            return self.render_ansi()
        elif color_scheme == 'bbcode':
            return self.render_bbcode()
        else:
            return self.render_text()

    def __repr__(self) -> str:
        return f"<TextObject type='{self.__class__.__name__}' @{id(self)}>"


class FileName(TextObject):
    def __init__(self, filename: str):
        color = AnsiColor.MAGENTA if filename.startswith('<') else AnsiColor.BLUE
        super().__init__(filename, color=color, style=AnsiStyle.BOLD)

    def __repr__(self) -> str:
        return f"<TextObject type='filename' @{id(self)}>"


class LineSeparator(TextObject):
    def __init__(self):
        super().__init__(':', color=AnsiColor.BLUE, style=AnsiStyle.DIM)

    def __repr__(self) -> str:
        return "<TextObject type='line_separator' @{}>".format(id(self))


class LineNumber(TextObject):
    @staticmethod
    def _pad_lineno(lineno: int) -> str:
        width = 3
        while width < len(str(lineno)):
            width += 3
        return '{:<{}}'.format(lineno, width)

    def __init__(self, number: int):
        padded = self._pad_lineno(number)
        super().__init__(padded, color=AnsiColor.BLUE, style=AnsiStyle.DIM)

    def __repr__(self) -> str:
        return "<TextObject type='lineno' @{}>".format(id(self))


class FuncnameSeparator(TextObject):
    def __init__(self):
        super().__init__(' ')

    def __repr__(self) -> str:
        return "<TextObject type='funcname_separator' @{}>".format(id(self))


class Funcname(TextObject):
    def __init__(self, funcname: str):
        display_name = funcname if funcname.startswith('<') else funcname + '()'
        super().__init__(display_name, color=AnsiColor.GREEN)

    def __repr__(self) -> str:
        return "<TextObject type='funcname' @{}>".format(id(self))


class BodySeparator(TextObject):
    def __init__(self):
        super().__init__('|', color=AnsiColor.BRIGHT_BLACK)

    def __repr__(self) -> str:
        return "<TextObject type='body_separator' @{}>".format(id(self))


class InBodySeparator(TextObject):
    def __init__(self):
        super().__init__(';', color=AnsiColor.BRIGHT_BLACK)

    def __repr__(self) -> str:
        return "<TextObject type='inbody_separator' @{}>".format(id(self))


class BodyPart(TextObject):
    def __init__(self, data: str, color: str = '', style: str = ''):
        super().__init__(data, color=color, style=style)

    def __repr__(self) -> str:
        return "<TextObject type='body_part' @{}>".format(id(self))


class IndexMarker(TextObject):
    def __init__(self, value: int = 0, scope: Optional[str] = None):
        from .scope import counter
        if scope is not None:
            # If scope is provided, use it
            value = counter.update_scoped(scope)
        elif value == 0:
            counter.reset_all()
        super().__init__('[{}]'.format(value), color=AnsiColor.RED)
    
    def __repr__(self) -> str:
        return "<TextObject type='index' @{}>".format(id(self))


class Space(TextObject):
    def __init__(self, count: int = 1):
        super().__init__(' ' * count)

    def __repr__(self) -> str:
        return "<TextObject type='space' @{}>".format(id(self))


class ProgressBar(TextObject):
    _BAR_LENGTH = 40
    _FILLED_CHAR = '─'
    _EMPTY_CHAR = '─'
    _DEBUG_FILLED_CHAR = '█'
    _DEBUG_EMPTY_CHAR = '▁'
    
    def __init__(self, current: int, total: int, color: str = AnsiColor.RED, filled_char: Optional[str] = None, empty_char: Optional[str] = None):
        self.current = current
        self.total = total
        self.filled_char = filled_char if filled_char is not None else self._FILLED_CHAR
        self.empty_char = empty_char if empty_char is not None else self._EMPTY_CHAR
        
        assert len(self.filled_char) == 1, "filled_char must be a single character"
        assert len(self.empty_char) == 1, "empty_char must be a single character"
        
        progress = min(current, total) / total if total else 0
        filled = int(progress * self._BAR_LENGTH)
        self.filled_length = filled
        self.empty_length = self._BAR_LENGTH - filled
        
        data = self.filled_char * self.filled_length + self.empty_char * self.empty_length
        super().__init__(data, color=color)

    def render_ansi(self) -> str:
        if console.debugger.enabled:
            filled_part = color_text(self._DEBUG_FILLED_CHAR * self.filled_length, self.color)
            empty_part = color_text(self._DEBUG_EMPTY_CHAR * self.empty_length, AnsiColor.BRIGHT_BLACK)
            return filled_part + empty_part
        else:
            filled_part = color_text(self.filled_char * self.filled_length, self.color)
            empty_part = color_text(self.empty_char * self.empty_length, AnsiColor.BRIGHT_BLACK)
            return filled_part + empty_part

    def render_text(self) -> str:
        if console.debugger.enabled:
            return self._DEBUG_FILLED_CHAR * self.filled_length + self._DEBUG_EMPTY_CHAR * self.empty_length
        else:
            return self.filled_char * self.filled_length + self.empty_char * self.empty_length

    def __repr__(self) -> str:
        return "<TextObject type='progress_bar' @{}>".format(id(self))


class DividerLine(TextObject):
    _LEVEL_CHARS = {
        1: '─',
        2: '█',
    }
    
    def __init__(
        self, 
        body_text: str = '', 
        level: int = 1,
        color: str = AnsiColor.YELLOW,
        console_width: Optional[int] = None,
        header_text: str = '',
        index: Optional[int] = None,
        show_name: Optional[bool] = None,
    ):
        self.level = level
        self.body_text = body_text
        self.header_text = header_text
        self.index = index
        self.show_name = show_name
        
        if console_width is None:
            from .console import get_console_width
            console_width = get_console_width()
        
        line_char = self._LEVEL_CHARS.get(level, '─')
        
        separator = '| '
        space_around_body = 1
        
        # Calculate index part
        index_part = ''
        if index is not None:
            index_part = f'[{index}] '
        
        header_len = len(header_text) + len(separator) + len(index_part)
        
        if body_text:
            body_len = len(body_text)
            available_width = console_width - header_len - body_len - 2 * space_around_body
            
            if available_width <= 0:
                left_line_len = 0
                right_line_len = 0
            else:
                left_line_len = available_width // 2
                right_line_len = available_width - left_line_len
            
            left_line = line_char * left_line_len
            right_line = line_char * right_line_len
            
            data = f'{header_text}{separator}{index_part}{left_line}{" " * space_around_body}{body_text}{" " * space_around_body}{right_line}'
        else:
            # No body text, full width divider
            available_width = console_width - header_len
            left_line_len = available_width
            right_line_len = 0
            
            left_line = line_char * left_line_len
            right_line = ''
            
            data = f'{header_text}{separator}{index_part}{left_line}'
        
        super().__init__(data, color=color)

    def render_ansi(self) -> str:
        if self.level == 0:
            return self.body_text
        
        separator = f'\033[0;90m| \033[0m'
        line_char = self._LEVEL_CHARS.get(self.level, '─')
        space_around_body = 1
        
        # Calculate index part
        index_part = ''
        if self.index is not None:
            index_part = f'\033[0;{AnsiColor.RED}m[{self.index}]\033[0m '
        
        console_width = len(self._data)
        header_len = len(self.header_text) + len('| ') + len(index_part.replace('\033[0;91m', '').replace('\033[0m', ''))
        
        if self.body_text:
            body_len = len(self.body_text)
            available_width = console_width - header_len - body_len - 2 * space_around_body
            
            if available_width <= 0:
                left_line_len = 0
                right_line_len = 0
            else:
                left_line_len = available_width // 2
                right_line_len = available_width - left_line_len
            
            if self.color:
                left_line = f'\033[0;{self.color}m{line_char * left_line_len}\033[0m'
                right_line = f'\033[0;{self.color}m{line_char * right_line_len}\033[0m'
            else:
                left_line = line_char * left_line_len
                right_line = line_char * right_line_len
            
            body = self.body_text
            
            return f'{self.header_text}{separator}{index_part}{left_line}{" " * space_around_body}{body}{" " * space_around_body}{right_line}'
        else:
            # No body text, full width divider
            available_width = console_width - header_len
            left_line_len = available_width
            
            if self.color:
                left_line = f'\033[0;{self.color}m{line_char * left_line_len}\033[0m'
            else:
                left_line = line_char * left_line_len
            
            return f'{self.header_text}{separator}{index_part}{left_line}'

    def render_bbcode(self) -> str:
        if self.level == 0:
            return self.body_text
        
        separator = '[bright_black]|[/] '
        line_char = self._LEVEL_CHARS.get(self.level, '─')
        space_around_body = 1
        
        # Calculate index part
        index_part = ''
        if self.index is not None:
            index_part = f'[red][{self.index}][/] '
        
        console_width = len(self._data)
        header_len = len(self.header_text) + len('| ') + len(index_part.replace('[red]', '').replace('[/]', ''))
        
        if self.body_text:
            body_len = len(self.body_text)
            available_width = console_width - header_len - body_len - 2 * space_around_body
            
            if available_width <= 0:
                left_line_len = 0
                right_line_len = 0
            else:
                left_line_len = available_width // 2
                right_line_len = available_width - left_line_len
            
            if self.color:
                bbcode_color = self._ansi_to_bbcode.get(self.color, 'white')
                left_line = f'[{bbcode_color}]{line_char * left_line_len}[/]'
                right_line = f'[{bbcode_color}]{line_char * right_line_len}[/]'
            else:
                left_line = line_char * left_line_len
                right_line = line_char * right_line_len
            
            body = self.body_text
            
            return f'{self.header_text}{separator}{index_part}{left_line}{" " * space_around_body}{body}{" " * space_around_body}{right_line}'
        else:
            # No body text, full width divider
            available_width = console_width - header_len
            left_line_len = available_width
            
            if self.color:
                bbcode_color = self._ansi_to_bbcode.get(self.color, 'white')
                left_line = f'[{bbcode_color}]{line_char * left_line_len}[/]'
            else:
                left_line = line_char * left_line_len
            
            return f'{self.header_text}{separator}{index_part}{left_line}'

    def __repr__(self) -> str:
        return "<TextObject type='divider_line' @{}>".format(id(self))


class Indicator(TextObject):
    def __init__(
        self,
        current: int,
        total: int,
        style: t.Literal['counter', 'digital', 'decimal', 'none'] = 'counter',
        color: str = AnsiColor.RED
    ):
        self.current = current
        self.total = total
        self.style = style
        self.color = color
        
        if style == 'none' or total is None:
            data = ""
        elif style == 'counter':
            total_len = len(str(total))
            current_str = str(current).rjust(total_len)
            data = f"[{current_str}/{total}]"
        elif style == 'digital':
            percentage = int((current / total) * 100) if total else 0
            data = f"[{percentage:>3}%]"
        elif style == 'decimal':
            percentage = (current / total) * 100 if total else 0
            data = f"[{percentage:>6.2f}%]"
        else:
            data = ""
        
        super().__init__(data, color=color)

    def __repr__(self) -> str:
        return "<TextObject type='indicator' @{}>".format(id(self))


class LeftPartDividerLine(TextObject):
    def __init__(self, level: int = 1, color: str = ''):
        # We can't calculate actual length yet - this will be handled later
        # For now, just initialize with a placeholder
        line_char = '─' if level == 1 else '█'
        self.level = level
        self._divider_color = color  # 只有明确传入颜色时才设置
        super().__init__('', color=color)
    
    def __repr__(self) -> str:
        return "<TextObject type='left_part_divider_line' @{}>".format(id(self))


class RightPartDividerLine(TextObject):
    def __init__(self, level: int = 1, color: str = ''):
        line_char = '─' if level == 1 else '█'
        self.level = level
        self._divider_color = color  # 只有明确传入颜色时才设置
        super().__init__('', color=color)
    
    def __repr__(self) -> str:
        return "<TextObject type='right_part_divider_line' @{}>".format(id(self))


class FullDimmedDividerLine(TextObject):
    def __init__(self, level: int = 1):
        line_char = '─' if level == 1 else '█'
        self.level = level
        # We can't calculate actual length yet
        super().__init__('', color=AnsiColor.BRIGHT_BLACK)
    
    def __repr__(self) -> str:
        return "<TextObject type='full_dimmed_divider_line' @{}>".format(id(self))


class VarnamedBodyPart(TextObject):
    def __init__(self, varname: str, value: Any, color: str = '', style: str = ''):
        from .formatter import formatter
        data = f'{varname} = {formatter._format_value(value)}'
        super().__init__(data, color=color, style=style)
    
    def __repr__(self) -> str:
        return "<TextObject type='varnamed_body_part' @{}>".format(id(self))
