from inspect import currentframe

from rich.pretty import pprint

from .frame import FrameInfo


class _Debugger:
    def __init__(self) -> None:
        self.debug_output = False
        self.debug_print = False
        self.output = []

    @property
    def enabled(self) -> bool:
        return self.debug_output

    def print(self, *args) -> None:
        if self.debug_print:
            frame = FrameInfo(currentframe().f_back)  # type: ignore
            pprint(
                (
                    '[npdbg]:{}:{}'.format(frame.file_name, frame.line_number),
                    *args,
                )
            )


debugger = _Debugger()
