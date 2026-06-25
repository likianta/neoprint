import builtins
import os
import sys
import typing as tp

from rich.console import Console as RichConsole

from .debugger import debugger

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


class _LegacyRichConsole(RichConsole):
    def __init__(self) -> None:
        # https://github.com/Textualize/rich/issues/2622
        super().__init__(
            color_system='standard' if os.name == 'nt' else 'auto',
            legacy_windows=True,
        )

    def capture_output(self, *args, **kwargs) -> str:
        # https://chatgpt.com/share/6a16a585-0e00-8320-97ee-5fc2b572690e
        with self.capture() as cap:
            self.print(*args, **kwargs)
        return cap.get()


class _ModernRichConsole(_LegacyRichConsole):
    def __init__(self) -> None:
        RichConsole.__init__(
            self,
            color_system='standard' if os.name == 'nt' else 'auto',
            legacy_windows=False,  # make sure ansi color is used
        )


console = Console()
# CONSOLE_WIDTH = console.width
rich_console = _ModernRichConsole()
legacy_rich_console = _LegacyRichConsole()

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
