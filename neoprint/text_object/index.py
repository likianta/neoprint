from .base import T
from .base import TextObject
from ..render import render


class Index(TextObject):
    def __init__(self, index: int) -> None:
        self._text = '[{}]'.format(index)
        self.editable = False

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render((self._text, 'red'), code_scheme=color_code_scheme)

