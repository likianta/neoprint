from .base import T
from .base import TextObject
from ..render import render


class Index(TextObject):
    def __init__(self, index: int) -> None:
        self._text = '[{}]'.format(index)
        self.color = 'red'
        self.style = ''
        # self.editable = False

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        return render(
            (self._text, self.color, self.style),  # type: ignore
            color_code_scheme=color_code_scheme,
        )
