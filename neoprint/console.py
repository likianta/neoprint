import os
import sys


class _Debug:
    def __init__(self):
        self.enabled = False
        self.output = []


debug = _Debug()


ANSI_ESCAPE = '\033['
ANSI_RESET = ANSI_ESCAPE + '0m'


class AnsiColor:
    BLACK = '30'
    RED = '31'
    GREEN = '32'
    YELLOW = '33'
    BLUE = '34'
    MAGENTA = '35'
    CYAN = '36'
    WHITE = '37'
    DEFAULT = '39'

    BRIGHT_BLACK = '90'
    BRIGHT_RED = '91'
    BRIGHT_GREEN = '92'
    BRIGHT_YELLOW = '93'
    BRIGHT_BLUE = '94'
    BRIGHT_MAGENTA = '95'
    BRIGHT_CYAN = '96'
    BRIGHT_WHITE = '97'


class AnsiStyle:
    RESET = '0'
    BOLD = '1'
    DIM = '2'
    ITALIC = '3'
    UNDERLINE = '4'


LEVEL_COLORS = {
    0: '',
    1: AnsiColor.BRIGHT_BLACK,
    2: AnsiColor.CYAN,
    3: AnsiColor.GREEN,
    4: AnsiColor.BRIGHT_GREEN,
    5: AnsiColor.YELLOW,
    6: AnsiColor.BRIGHT_YELLOW,
    7: AnsiColor.RED,
    8: AnsiColor.BRIGHT_RED,
    9: AnsiColor.BRIGHT_WHITE,
}


def _apply_style(color: str, style: str = '') -> str:
    style_code = style + ';' if style else ''
    return ANSI_ESCAPE + '0;' + style_code + color + 'm'


def color_text(text: str, color: str, style: str = '') -> str:
    return _apply_style(color, style) + text + ANSI_RESET


def get_console_width() -> int:
    if hasattr(sys.stdout, 'columns'):
        columns = sys.stdout.columns
        if columns:
            return int(columns)  # type: ignore
    if hasattr(os, 'get_terminal_size'):
        try:
            size = os.get_terminal_size()
            if size.columns > 0:
                return int(size.columns)
        except OSError:
            pass
    fallback = os.environ.get('COLUMNS', '')
    if fallback.isdigit():
        return int(fallback)
    return 80


CONSOLE_WIDTH = get_console_width()


def print(
    *args: object, sep: str = ' ', end: str = '\n', flush: bool = False
) -> None:
    output = sep.join(str(arg) for arg in args) + end
    if debug.enabled:
        debug.output.append(output)
    try:
        sys.stdout.write(output)
        if flush:
            sys.stdout.flush()
    except IOError:
        pass


def clear_line() -> None:
    sys.stdout.write('\r' + ANSI_ESCAPE + 'K' + ANSI_RESET)
    sys.stdout.flush()
