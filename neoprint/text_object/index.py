from .base import T
from .base import TextObject
from ..render import render


class Index(TextObject):
    def __init__(self, index: int, color: str = 'red') -> None:
        self._text = '[{}]'.format(index)
        self.color = color  # type: ignore
        #   notice: color is related to `../markup.py:MarkupAnalyzer:analyze`
        #   and `../scope/counter.py:Counter:get_color_by_frame`. the color 
        #   may be 'default', 'red', or '#' followed with random 6 hex digits.
        #   we need to render the last case carefully.
        self.style = ''

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        return render(
            (self._text, self.color, self.style),  # type: ignore
            color_code_scheme=color_code_scheme,
            true_color_mode=self.color.startswith('#'),
        )
