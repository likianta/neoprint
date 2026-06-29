import typing as t

from ..render import T


class TextObject:
    color: T.Color = 'default'
    # color: t.Union[t.Literal[''], T.Color] = ''
    editable: bool = True
    #   whether do `color` and `style` can be changed after `__init__`.
    style: T.Style = ''

    def __len__(self) -> int:
        return len(self.render(color_code_scheme='plain'))

    def render(self, *_, **__) -> str:
        raise NotImplementedError


class TextObjectGroup(TextObject):
    editable: bool = True
    _color: T.Color = 'default'
    _objs: t.List[TextObject]
    _style: T.Style = ''

    def __init__(self) -> None:
        self._objs = []

    @property
    def color(self) -> T.Color:
        return self._color

    @color.setter
    def color(self, value: T.Color) -> None:
        self._color = value
        for x in self._objs:
            if x.editable:
                x.color = value

    @property
    def style(self) -> T.Style:
        return self._style

    @style.setter
    def style(self, value: T.Style) -> None:
        self._style = value
        for x in self._objs:
            if x.editable:
                x.style = value

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        return ''.join(
            x.render(color_code_scheme=color_code_scheme) for x in self._objs
        )
