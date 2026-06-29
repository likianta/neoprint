import sys
import typing as tp
from types import TracebackType

from rich.traceback import Traceback

from .base import T
from .base import TextObject
from .text import Text
from ..console import legacy_rich_console
from ..console import rich_console


class ExceptionLine(Text):
    def __init__(self, exception: BaseException):
        super().__init__(str(exception), color='red')


class ExceptionPanel(TextObject):
    @classmethod
    def from_sys_exc(cls, show_locals: bool = False) -> 'ExceptionPanel':
        exc_info = sys.exc_info()
        assert all(exc_info)
        return cls(
            exception=exc_info[1],  # type: ignore
            show_locals=show_locals,
            _exception_type=exc_info[0],
            _exception_traceback=exc_info[2],
        )

    def __init__(
        self,
        exception: BaseException,
        show_locals: bool = False,
        _exception_type: tp.Optional[type] = None,
        _exception_traceback: tp.Optional[TracebackType] = None,
    ) -> None:
        self._show_locals = show_locals
        self._exc_type = _exception_type or type(exception)
        self._exc_value = exception
        self._exc_tb = _exception_traceback or exception.__traceback__

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        tb = Traceback.from_exception(
            self._exc_type,
            self._exc_value,
            self._exc_tb,
            show_locals=self._show_locals,
            locals_hide_dunder=True,
            locals_hide_sunder=True,
        )
        if color_code_scheme == 'plain':
            return legacy_rich_console.capture_output(tb).rstrip()
        elif color_code_scheme == 'ansi':
            return rich_console.capture_output(tb).rstrip()
        else:
            raise NotImplementedError
