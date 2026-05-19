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
    old_print = console.print
    output_list: list[str] = []

    class CapturedOutput:
        def __init__(self):
            self._output_list = output_list
            self._color_code_scheme = color_code_scheme
            self._processed_output = None
        
        @property
        def output(self):
            if self._processed_output is None:
                processed = []
                for line in self._output_list:
                    if self._color_code_scheme == 'none':
                        from .console import strip_ansi
                        line = strip_ansi(line)
                    processed.append(line)
                self._processed_output = processed
            return self._processed_output
    
    captured = CapturedOutput()

    # 重写 print 方法，确保每次调用 console.print 都添加到列表中
    def capturing_print(*args, sep=' ', end='\n', flush=False):
        text = sep.join(str(arg) for arg in args)
        output_list.append(text)  # 保存不包含 end 的 text
        full_text = text + end
        old_stdout.write(full_text)
        if flush:
            old_stdout.flush()

    try:
        console.print = capturing_print
        yield captured
    finally:
        console.print = old_print

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
