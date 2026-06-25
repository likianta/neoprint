import typing as t

from .base import T
from .base import TextObject
from ..render import render


class Text(TextObject):
    def __init__(
        self, obj: t.Any, color: T.Color = 'default', style: T.Style = ''
    ) -> None:
        self._origin = obj
        self._text = str(obj)
        self.color = color
        self.style = style

    def __str__(self) -> str:
        return self._text

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        color = self.color
        if color == 'default':
            if self._origin is True:
                color = 'green'
            elif self._origin is False:
                color = 'red'
            elif self._origin is None:
                color = 'magenta'
        return render(
            (self._text, color, self.style), color_code_scheme=color_code_scheme
        )
