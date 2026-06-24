import textwrap as tw

import rich.jupyter
import rich.markdown

from .base import T
from .base import TextObject
from ..console import legacy_rich_console
from ..console import rich_console


class RichObject(TextObject):
    def __init__(self, obj: rich.jupyter.JupyterMixin) -> None:
        self._obj = obj
        self.editable = False

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        # https://chatgpt.com/share/6a16a585-0e00-8320-97ee-5fc2b572690e
        if color_code_scheme == 'none':
            return legacy_rich_console.capture_output(self._obj).rstrip()
        elif color_code_scheme == 'ansi':
            return rich_console.capture_output(self._obj).rstrip()
        else:
            raise NotImplementedError


class Markdown(RichObject):
    def __init__(self, text: str) -> None:
        super().__init__(rich.markdown.Markdown(tw.dedent(text)))
