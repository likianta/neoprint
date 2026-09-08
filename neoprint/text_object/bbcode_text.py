from .base import T
from .base import TextObjectGroup
from .text import Text
# from ..console import dbg_print
from ..render import translate


class BBCodeText(TextObjectGroup):
    def __init__(self, text: str) -> None:
        # self._objs = [Text(*x) for x in translate(text)]

        self._objs = []
        for each in translate(text):
            # dbg_print(each)
            obj = Text(*each)
            if each[1] != 'default':
                obj.editable = False
            self._objs.append(obj)
        self.editable = True

    # @property
    # def color(self) -> T.Color:
    #     return self._color

    # @color.setter
    # def color(self, value: T.Color) -> None:
    #     self._color = value
    #     for x in self._objs:
    #         if x.editable:
    #             x.color = value

    @property
    def style(self) -> T.Style:
        return self._style

    @style.setter
    def style(self, value: T.Style) -> None:
        self._style = value
        for x in self._objs:
            # if x.color == 'default' but x.style != '', though it declares as 
            # editable, we don't change its style.
            # see `test/bbcode_text.py:nested_bbcode:3rd line`.
            if x.editable and not x.style:
                x.style = value
