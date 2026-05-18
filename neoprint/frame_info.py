import inspect
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .sourcemap import get_source_lines, get_varnames


@dataclass
class FrameInfo:
    filepath: str
    lineno: int
    funcname: str
    code_context: Optional[str] = None
    _varnames: Optional[Tuple[str, ...]] = None

    @property
    def id(self) -> str:
        return self.filepath + ':' + str(self.lineno)

    @property
    def filename(self) -> str:
        return os.path.basename(self.filepath)

    @property
    def relpath(self) -> str:
        return self.filepath

    @property
    def source_line(self) -> str:
        try:
            lines = get_source_lines(self.filepath, self.lineno)
            if lines:
                return lines[0].strip()
        except Exception:
            pass
        return ''

    @property
    def varnames(self) -> Tuple[str, ...]:
        if self._varnames is not None:
            return self._varnames
        try:
            return get_varnames(self.filepath, self.lineno)
        except Exception:
            return ()

    @varnames.setter
    def varnames(self, value: Tuple[str, ...]) -> None:
        self._varnames = value

    def get_parent(self, level: int = 1) -> Optional['FrameInfo']:
        try:
            frame = inspect.currentframe()
            for _ in range(level + 1):
                if frame is None:
                    return None
                frame = frame.f_back
            if frame is None:
                return None
            return from_frame(frame)
        except Exception:
            return None


def from_frame(frame) -> FrameInfo:
    code = frame.f_code
    filepath = frame.f_globals.get('__file__', code.co_filename)
    if filepath.startswith('<') and filepath.endswith('>'):
        filepath = '<' + filepath[1:-1] + '@' + str(id(frame)) + '>'
    else:
        filepath = os.path.abspath(filepath)
    funcname = code.co_name
    lineno = frame.f_lineno
    code_context = None
    try:
        info = inspect.getframeinfo(frame)
        if info.code_context:
            code_context = info.code_context[0].strip()
    except Exception:
        pass
    return FrameInfo(
        filepath=filepath,
        lineno=lineno,
        funcname=funcname,
        code_context=code_context,
    )


def get_caller_frame(extra_levels: int = 0) -> Optional[FrameInfo]:
    try:
        frame = inspect.currentframe()
        if frame is None:
            return None
        levels = 2 + extra_levels
        for _ in range(levels):
            frame = frame.f_back
            if frame is None:
                return None
        return from_frame(frame)
    except Exception:
        return None


def get_call_stack(limit: int = 10) -> List[FrameInfo]:
    frames = []
    try:
        frame = inspect.currentframe()
        if frame is None:
            return frames
        for _ in range(limit):
            frame = frame.f_back
            if frame is None:
                break
            frames.append(from_frame(frame))
    except Exception:
        pass
    return frames
