from inspect import currentframe

from rich.pretty import pprint


class _Debugger:
    def __init__(self) -> None:
        self.enabled = False
        self.output = []

    def print(self, *args) -> None:
        from .frame import FrameInfo

        frame = FrameInfo(currentframe().f_back)  # type: ignore
        pprint(
            (
                '[npdebug]:{}:{}'.format(frame.file_name, frame.line_number),
                *args,
            )
        )


debugger = _Debugger()
