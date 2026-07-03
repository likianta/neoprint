import typing as tp

from .base import TextObject


class Origin(TextObject):
    def __init__(self, obj: tp.Any) -> None:
        self._obj = obj

    def render(self, *_, **__) -> str:
        return str(self._obj)
