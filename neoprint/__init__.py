from . import util
from .capture import capture_output
from .config import config
from .console import (
    AnsiColor,
    AnsiStyle,
    color_text,
    debugger,
    get_console_width,
)
from .format import format
from .formatter import formatter
from .frame_info import FrameInfo
from .markup import MarkupParser, ParsedMarks
from .progress import Progress
from .scope import get_current_scope, scope
from .show import (
    show,
    print as print,
    debug as debug,
    info as info,
    success as success,
    warning as warning,
    error as error,
)


# Add config support for debug_output:
def _set_debug_output(value: bool):
    debugger.enabled = value


original_config = config


def new_config(**kwargs):
    if 'debug_output' in kwargs:
        _set_debug_output(kwargs.pop('debug_output'))
    if kwargs:
        original_config(**kwargs)


config = new_config


__all__ = [
    'AnsiColor',
    'AnsiStyle',
    'FrameInfo',
    'MarkupParser',
    'ParsedMarks',
    'Progress',
    'capture_output',
    'color_text',
    'config',
    'debug',
    'debugger',
    'error',
    'format',
    'formatter',
    'get_console_width',
    'get_current_scope',
    'info',
    'print',
    'scope',
    'show',
    'success',
    'util',
    'warning',
]

__version__ = '0.1.0'
