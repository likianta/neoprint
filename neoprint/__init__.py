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
    'scope',
]


def format(*args, markup: str = '', color_code_scheme: str = 'none') -> str:
    import inspect
    from .show import counter

    if args and isinstance(args[0], str) and args[0].startswith(':'):
        markup = args[0]
        args = args[1:]
    elif args and isinstance(args[-1], str) and args[-1].startswith(':'):
        markup = args[-1]
        args = args[:-1]

    frame = inspect.currentframe()
    caller_frame = frame.f_back if frame is not None else None
    caller_filepath = caller_frame.f_code.co_filename if caller_frame is not None else None
    caller_lineno = caller_frame.f_lineno if caller_frame is not None else None

    parser = MarkupParser()
    marks = parser.parse(markup) if markup else ParsedMarks()

    index_value = None
    if marks.index is not None:
        if marks.index == 0:
            counter.reset_all()
            index_value = None
        elif marks.index == 1:
            line_key = f"{caller_filepath}:{caller_lineno}"
            index_value = counter.update_line(line_key)
        elif marks.index == 2:
            current_scope = counter.get_current_scope()
            if current_scope:
                scope_id = current_scope
            else:
                scope_id = caller_frame.f_code.co_name if caller_frame else '<module>'
            index_value = counter.update_scoped(scope_id)
        elif marks.index == 3:
            index_value = counter.update_global()

    return formatter.format(
        *args,
        markup=markup,
        color_code_scheme=color_code_scheme,
        _caller_filepath=caller_filepath,
        _caller_lineno=caller_lineno,
        _index_value=index_value,
        _index=marks.index,
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


import uuid
from .show import counter


@contextmanager
def scope(name: str = None):
    if name is None:
        name = str(uuid.uuid4())[:8]
    counter.push_scope(name)
    try:
        yield name
    finally:
        counter.pop_scope()


def get_current_scope() -> str:
    return counter.get_current_scope()
