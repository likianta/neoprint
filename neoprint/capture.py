from contextlib import contextmanager
import sys
from typing import Callable, List

from . import console
from .console import strip_ansi


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


def ansi_to_bbcode(text: str) -> str:
    """将 ANSI 转义序列转换为 bbcode 格式"""
    result = []
    i = 0
    n = len(text)
    open_tags = []

    while i < n:
        if i + 1 < n and text[i] in '\x1b\x033' and text[i + 1] == '[':
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
    def __init__(self, output_list: List[str], color_code_scheme: str):
        self._output_list = output_list
        self._color_code_scheme = color_code_scheme
        self._processed_output = None

    @property
    def output(self) -> List[str]:
        if self._processed_output is None:
            processed = []
            for line in self._output_list:
                if self._color_code_scheme == 'none':
                    line = strip_ansi(line)
                elif self._color_code_scheme == 'ascii':
                    line = line.replace('\033', '\\x1b')
                    line = line.replace('\x1b', '\\x1b')
                elif self._color_code_scheme == 'bbcode':
                    line = ansi_to_bbcode(line)
                processed.append(line)
            self._processed_output = processed
        return self._processed_output


@contextmanager
def capture_output(color_code_scheme: str = 'none'):
    old_stdout = sys.stdout
    old_print = console.print
    output_list: List[str] = []

    def capturing_print(
        *args: object, sep: str = ' ', end: str = '\n', flush: bool = False
    ) -> None:
        text = sep.join(str(arg) for arg in args)
        output_list.append(text)
        full_text = text + end
        old_stdout.write(full_text)
        if flush:
            old_stdout.flush()

    try:
        console.print = capturing_print  # type: ignore
        yield CapturedOutput(output_list, color_code_scheme)
    finally:
        console.print = old_print
