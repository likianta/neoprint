from .base import TextObjectGroup
from .text import Text
from ..render import translate


class BBCodeText(TextObjectGroup):
    def __init__(self, text: str):
        self._objs = [Text(*x) for x in translate(text)]
