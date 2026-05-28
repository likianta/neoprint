from inspect import currentframe
from rich.pretty import pprint
from .frame_info import FrameInfo


class _Debugger:
    def __init__(self) -> None:
        self.enabled = False
        self.output = []

    def print(self, *args) -> None:
        frame = FrameInfo(currentframe().f_back)  # type: ignore
        pprint(
            ('[debug]:{}:{}'.format(frame.file_name, frame.line_number), *args)
        )


debugger = _Debugger()
