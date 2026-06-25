from .base import T
from .base import TextObject
from ..render import render


class BodySeparator(TextObject):
    def __init__(self, char: str = '|') -> None:
        self._char = char

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        return render(
            (self._char, 'default', 'dim'), color_code_scheme=color_code_scheme
        )


FuncnameSeparator = BodySeparator


class InBodySeparator(TextObject):
    def __init__(self, char: str = ';') -> None:
        self._sep = char

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        return render(
            (self._sep, self.color, 'dim'), color_code_scheme=color_code_scheme
        )
