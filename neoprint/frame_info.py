import inspect
import typing as tp
from textwrap import dedent
from types import FrameType

from . import sourcemap


class FrameInfo:
    file_name: str
    file_path: str
    function_name: str
    line_number: int
    package_name: str
    _frame: FrameType
    _varnames: tp.Optional[tp.Tuple[tp.Optional[str], ...]]

    @classmethod
    def this_place(cls) -> 'FrameInfo':
        return cls(inspect.currentframe().f_back)  # type: ignore

    @classmethod
    def parent_place(cls) -> 'FrameInfo':
        return cls(inspect.currentframe().f_back.f_back)  # type: ignore

    def __init__(self, frame: FrameType) -> None:
        self._frame = frame
        self.refresh()

    def __str__(self) -> str:
        return self.info

    @property
    def id(self) -> str:
        return f'{self.file_path}:{self.line_number}'

    @property
    def indentation(self) -> int:
        # https://stackoverflow.com/a/39172552
        if x := inspect.getframeinfo(self._frame).code_context:
            ctx = x[0]
            return len(ctx) - len(ctx.lstrip())
        return 0

    @property
    def info(self) -> str:
        return dedent(
            f"""
            <FrameInfo object
                filepath: {self.file_path}
                lineno: {self.line_number}
                funcname: {self.function_name}
            >
            """
        ).rstrip()

    @property
    def parent(self) -> 'FrameInfo':
        return self.get_parent(1)

    @property
    def varnames(self) -> tp.Sequence[tp.Optional[str]]:
        if self._varnames is None:
            self._varnames = tuple(self.collect_varnames())
        return self._varnames

    def collect_varnames(self) -> tp.Sequence[tp.Optional[str]]:
        return sourcemap.get_varnames(self.file_path, self.line_number)

    def get_parent(self, traceback_level: int = 1) -> 'FrameInfo':
        frame = self._frame
        for _ in range(traceback_level):
            frame = frame.f_back  # type: ignore
        return FrameInfo(frame)  # type: ignore

    def refresh(self) -> None:
        frame = self._frame
        self.function_name = frame.f_code.co_name
        self.package_name = frame.f_globals['__name__'].split('.', 1)[0]
        self.file_path = (
            frame.f_globals.get('__file__', frame.f_code.co_filename)
            #   note:
            #   - path may be "<string>", "<unknown>" etc.
            #   - path may be "<ipython-input-10-5abb16185f48>" in ipython
            #   environment.
            #   - `co_filename` may be a relative python in python 3.8.
            #   - path may not exist.
        ).replace('\\', '/')
        self.file_name = (
            self.file_path
            if self.file_path[0] == '<'
            else self.file_path.rsplit('/', 1)[-1]
        )
        self.line_number = frame.f_lineno
        self._varnames = None
