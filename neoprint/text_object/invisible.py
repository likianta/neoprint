from .base import TextObject


class LineBreak(TextObject):
    def __init__(self, count: int = 1) -> None:
        self._count = count
        self.editable = False

    def render(self, **_) -> str:
        return '\n' * self._count


class Space(TextObject):
    def __init__(self, length: int = 1) -> None:
        self._length = length
        self.editable = False

    def render(self, **_) -> str:
        return ' ' * self._length
