import sys
from contextlib import contextmanager
from typing import List

from . import console
from .console import strip_ansi
from .util import ansi_to_bbcode


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
