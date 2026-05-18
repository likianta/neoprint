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
    'capture_output',
]


def format(*args, markup: str = '', color_code_scheme: str = 'none') -> str:
    import inspect
    frame = inspect.currentframe()
    caller_frame = frame.f_back if frame is not None else None
    caller_filepath = caller_frame.f_code.co_filename if caller_frame is not None else None
    caller_lineno = caller_frame.f_lineno if caller_frame is not None else None
    return formatter.format(
        *args,
        markup=markup,
        color_code_scheme=color_code_scheme,
        _caller_filepath=caller_filepath,
        _caller_lineno=caller_lineno
    )


from contextlib import contextmanager
from io import StringIO
import sys


@contextmanager
def capture_output(color_code_scheme: str = 'none'):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()

    class CapturedOutput:
        def __init__(self):
            self._stdout_buffer = stdout_buffer
            self._stderr_buffer = stderr_buffer
            self._color_code_scheme = color_code_scheme

        def __getitem__(self, index):
            if index == 0:
                val = self._stdout_buffer.getvalue().rstrip('\n')
            elif index == 1:
                val = self._stderr_buffer.getvalue().rstrip('\n')
            else:
                raise IndexError('list index out of range')
            if self._color_code_scheme == 'none':
                from .console import strip_ansi
                val = strip_ansi(val)
            return val

    captured = CapturedOutput()

    try:
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        yield captured
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        stdout_val = stdout_buffer.getvalue()
        stderr_val = stderr_buffer.getvalue()
        if color_code_scheme == 'none':
            from .console import strip_ansi
            stdout_val = strip_ansi(stdout_val)
            stderr_val = strip_ansi(stderr_val)
        stdout_val = stdout_val.rstrip('\n')
        stderr_val = stderr_val.rstrip('\n')
        captured._stdout_buffer = StringIO()
        captured._stdout_buffer.write(stdout_val)
        captured._stderr_buffer = StringIO()
        captured._stderr_buffer.write(stderr_val)

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
