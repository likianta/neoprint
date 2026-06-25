import typing as t

from .base import T
from .base import TextObject
from ..render import render


class NamedVariable(TextObject):
    def __init__(
        self, name: str, value: t.Any, *, _quote_string: bool = True
    ) -> None:
        self._name = name
        self._origin = value
        self._value = (
            self.quote_string(value)
            if _quote_string and isinstance(value, str)
            else str(value)
        )

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        color1 = self.color
        color2 = self.color
        if color2 == 'default':
            if self._value is True:
                color2 = 'green'
            elif self._value is False:
                color2 = 'red'
            elif self._value is None:
                color2 = 'magenta'
        return render(
            # (self._name + ' = ', color1, 'dim'),
            (self._name + ' = ', color1, self.style),
            (self._value, color2, self.style),
            color_code_scheme=color_code_scheme,
        )

    @staticmethod
    def quote_string(s: str) -> str:
        if s and s[0] == '"':
            return s
        else:
            return '"' + s.replace('"', '\\"') + '"'
