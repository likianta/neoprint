import os
import sys
import typing as tp
from sys import excepthook as _default_excepthook

from rich.traceback import Traceback

from .console import console
from .console import rich_console
from .debugger import debugger


class _Config:
    clear_unfinished_stream: bool
    console_width: int
    debug_output: bool
    debug_print: bool
    disable_varnames: bool
    #   if source code is obfuscated, disable parsing varnames.
    #   this is usually used with `pyportable-crypto` library.
    legacy_windows: bool
    #   if true, decrease console color effect.
    multiline_indent: int
    path_style: tp.Literal['filename', 'relpath'] = 'filename'
    #   'relpath' (default): show relative path.
    #       for external libraries, will show `[lib_name]/relpath:lineno`
    #   'filename': show only filename.
    #       for external libraries, will show `[lib_name]/filename:lineno`
    rich_traceback: bool
    show_funcname: bool
    show_source: bool
    #   attach source file path and line number info prefixed to the log -
    #   messages.
    #   True example:
    #       'main.py:10  >>  hello world'
    #   False example:
    #       'hello world'
    show_traceback_locals: bool
    show_varnames: bool
    #   show both variable names and values. (magic reflection)
    #   example:
    #       a, b = 1, 2
    #       logger.log(a, b, a + b)
    #       # enabled: 'main.py:11  >>  a = 1; b = 2; a + b = 3'
    #       # disabled: 'main.py:11  >>  1, 2, 3'
    show_verbosity_tag: bool
    #   example: print(':v8', 'some error happens')
    #   enabled: (red text) '[ERROR] some error happens'
    #   disabled: (red text) 'some error happens'
    sourcemap_alignment: tp.Literal['left', 'right'] = 'left'
    subthreaded: bool
    #   run lk logger in separate thread.

    _preset_conf: tp.Dict[str, tp.Union[bool, int, str]] = {
        'clear_unfinished_stream': False,
        'console_width': console.width,
        'debug_output': False,
        'debug_print': os.getenv('NEOPRINT_DEBUG') == '1',
        'disable_varnames': os.getenv('NEOPRINT_DISABLE_VARNAMES') == '1',
        'legacy_windows': os.getenv('NEOPRINT_LEGACY_WINDOWS') == '1',
        'multiline_indent': 2,
        'path_style': 'relpath',
        'rich_traceback': True,
        'show_funcname': False,
        'show_source': True,
        'show_traceback_locals': False,
        'show_varnames': False,
        'show_verbosity_tag': False,
        'sourcemap_alignment': 'left',
        'subthreaded': False,
    }

    def __init__(self) -> None:
        for k, v in self._preset_conf.items():
            self._apply(k, v)

    def __call__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            assert hasattr(self, k), k
            self._apply(k, v)

    def reset(self) -> None:
        for k, v in self._preset_conf.items():
            if getattr(self, k, None) != v:  # if None type, always skip it.
                # assert v is not None
                self._apply(k, v)

    def _apply(self, key: str, val: tp.Union[bool, int, str]) -> None:
        setattr(self, key, val)
        if key == 'console_width':
            assert isinstance(val, int)
            console.width = val
        elif key == 'debug_output':
            assert isinstance(val, bool)
            debugger.debug_output = val
        elif key == 'debug_print':
            assert isinstance(val, bool)
            debugger.debug_print = val
        elif key == 'disable_varnames':
            os.environ['NEOPRINT_DISABLE_VARNAMES'] = '1' if val else '0'
        elif key == 'legacy_windows':
            os.environ['NEOPRINT_LEGACY_WINDOWS'] = '1' if val else '0'
        elif key == 'rich_traceback':
            # assert isinstance(val, bool)
            if val:
                sys.excepthook = self._custom_excepthook
            else:
                sys.excepthook = _default_excepthook

    def _custom_excepthook(self, type_, value, traceback) -> None:
        # print(':r', '[red dim]drain out message queue[/]')
        # from .logger import logger
        # if hasattr(logger, '_stop_running'):
        #     logger._stop_running()  # noqa
        if type_ is KeyboardInterrupt:
            # fmt: off
            from .show import show
            show(':v7', 'KeyboardInterrupt')
            sys.exit(0)
            # fmt: on
        else:
            # https://rich.readthedocs.io/en/stable/traceback.html
            # dprint(getattr(self, 'show_traceback_locals'))
            rich_console.print(
                Traceback.from_exception(
                    type_,
                    value,
                    traceback,
                    show_locals=self.show_traceback_locals,
                    locals_hide_dunder=True,
                    locals_hide_sunder=True,
                    # word_wrap=True,
                ),
                soft_wrap=False,  # fixed line wrap problem.
            )


config = _Config()
