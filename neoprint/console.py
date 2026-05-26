import builtins
import os
import sys
import typing as tp
from inspect import currentframe
from rich.pretty import pprint

_stdout = sys.stdout


class Console:
    def __init__(self) -> None:
        self.width = self.get_console_width()

    def get_console_width(self) -> int:
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

    def print(self, text: str, end: str = '\n', flush: bool = False) -> None:
        if debugger.enabled:
            debugger.output.append(text)
        _stdout.write(text + end)
        if flush:
            _stdout.flush()


class _Debugger:
    def __init__(self) -> None:
        self.enabled = False
        self.output = []

    def print(self, *args) -> None:
        from .frame_info import FrameInfo

        frame = FrameInfo(currentframe().f_back)
        pprint(
            ('[debug]:{}:{}'.format(frame.file_name, frame.line_number), *args)
        )


console = Console()
# CONSOLE_WIDTH = console.width
debugger = _Debugger()

std_print = tp.cast(tp.Callable, builtins.print)
con_print = console.print
# con_error = partial(console.print_exception, word_wrap=True)
dbg_print = debugger.print
# non_print = NothingPrinter()

# alias
bprint = std_print
cprint = con_print
dprint = dbg_print

# default alias
# print = con_print
