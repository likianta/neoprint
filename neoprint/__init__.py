from .config import config
from .console import (
    AnsiColor,
    AnsiStyle,
    color_text,
    get_console_width,
    strip_ansi,
)
from .formatter import formatter
from .frame_info import FrameInfo
from .markup import MarkupParser, ParsedMarks
from .show import show

__all__ = [
    'show',
    'format',
    'config',
    'formatter',
    'color_text',
    'get_console_width',
    'strip_ansi',
    'AnsiColor',
    'AnsiStyle',
    'FrameInfo',
    'MarkupParser',
    'ParsedMarks',
]


def format(*args, markup: str = '', color_code_scheme: str = 'none') -> str:
    return formatter.format(*args, markup=markup, color_code_scheme=color_code_scheme)

__version__ = '0.1.0a8'


def get_body_string(*args, markup=''):
    import inspect

    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_filepath = caller_frame.f_code.co_filename
    caller_lineno = caller_frame.f_lineno

    return formatter.get_body_string(
        *args, markup=markup, _caller_filepath=caller_filepath,
        _caller_lineno=caller_lineno
    )
