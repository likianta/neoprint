from .config import config
from .console import (
    AnsiColor,
    AnsiStyle,
    color_text,
    get_console_width,
    strip_ansi,
    debug,
)
from .formatter import formatter
from .frame_info import FrameInfo
from .markup import MarkupParser, ParsedMarks
from .show import show
from . import util

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
    'debug',
    'util',
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
    
    # ANSI 颜色到 bbcode 的映射
    _ansi_color_to_bbcode = {
        '30': 'black',
        '31': 'red',
        '32': 'green',
        '33': 'yellow',
        '34': 'blue',
        '35': 'magenta',
        '36': 'cyan',
        '37': 'white',
        '90': 'bright_black',
        '91': 'red',
        '92': 'green',
        '93': 'yellow',
        '94': 'blue',
        '95': 'magenta',
        '96': 'cyan',
        '97': 'white',
    }

    def ansi_to_bbcode(text):
        """将 ANSI 转义序列转换为 bbcode 格式"""
        result = []
        i = 0
        n = len(text)
        open_tags = []
        
        while i < n:
            if (i + 1 < n and 
                text[i] in '\x1b\x033' and 
                text[i + 1] == '['):
                ansi_start = i
                i += 2
                m_pos = text.find('m', i)
                if m_pos != -1:
                    codes = text[i:m_pos].split(';')
                    i = m_pos + 1
                    
                    if len(codes) == 1 and codes[0] == '0':
                        for _ in range(len(open_tags)):
                            result.append('[/]')
                        open_tags.clear()
                        continue
                    
                    style = ''
                    color = None
                    for code in codes:
                        if code == '1':
                            style = 'bold '
                        elif code == '2':
                            style = 'dim '
                        elif code in _ansi_color_to_bbcode:
                            color = _ansi_color_to_bbcode[code]
                    
                    if color:
                        tag = f'[{style}{color}]'
                        open_tags.append(tag)
                        result.append(tag)
                else:
                    result.append(text[ansi_start:i])
            else:
                if text[i] == '[':
                    result.append('\\[')
                else:
                    result.append(text[i])
                i += 1
        
        for _ in range(len(open_tags)):
            result.append('[/]')
        
        return ''.join(result)

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
                    elif self._color_code_scheme == 'ascii':
                        # 将 ANSI 转义序列转义为 Python 字符串表示（使用十六进制 \x1b 格式）
                        line = line.replace('\033', '\\x1b')
                        line = line.replace('\x1b', '\\x1b')
                    elif self._color_code_scheme == 'bbcode':
                        # 将 ANSI 转换为 bbcode
                        line = ansi_to_bbcode(line)
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
