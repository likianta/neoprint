import re
import textwrap
import typing as t
from objprint import objstr
from .console import console
from .console import dprint  # noqa
from .frame_info import FrameInfo
from .path_glob import path_glob
from .render import T
from .render import render


class TextObject:
    color: T.Color = 'default'
    # color: t.Union[t.Literal[''], T.Color] = ''
    editable: bool = True
    #   whether do `color` and `style` can be changed after `__init__`.
    style: T.Style = ''

    def __len__(self) -> int:
        return len(self.render(color_code_scheme='none'))

    def render(self, *_, **__) -> str:
        raise NotImplementedError


class TextObjectGroup(TextObject):
    editable: bool = True
    _color: T.Color = 'default'
    _style: T.Style = ''
    _objs: t.List[TextObject] = []

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


# ------------------------------------------------------------------------------


class BodySeparator(TextObject):
    def __init__(self, char: str = '|') -> None:
        self._char = char

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render(
            (self._char, 'default', 'dim'), code_scheme=color_code_scheme
        )


class DividerLine(TextObject):
    def __init__(self, head, body, bold: bool = False) -> None:
        self._head = head
        self._body = body
        self._div_char = '█' if bold else '─'

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        body_space = console.width - sum(len(x) for x in self._head)
        if self._body:
            spare_space = body_space - sum(len(x) for x in self._body) - 2
            assert spare_space >= 2
            left_part_space = spare_space // 2
            right_part_space = (
                left_part_space if spare_space % 2 == 0 else left_part_space + 1
            )
            return ''.join(
                (
                    render(
                        (
                            self._div_char * left_part_space,
                            self.color,
                            self.style,
                        ),
                        (' ',),
                        code_scheme=color_code_scheme,
                    ),
                    *(
                        x.render(code_scheme=color_code_scheme)
                        for x in self._body
                    ),
                    render(
                        (' ',),
                        (
                            self._div_char * right_part_space,
                            self.color,
                            self.style,
                        ),
                        code_scheme=color_code_scheme,
                    ),
                )
            )
        else:
            spare_space = body_space
            assert spare_space > 0
            return render(
                (self._div_char * spare_space, self.color, 'dim'),
                code_scheme=color_code_scheme,
            )


class ExpandedObject(TextObjectGroup):
    @classmethod
    def check_expandable(cls, obj: TextObject) -> bool:
        return isinstance(obj, (RenderableObject, NamedVariable))

    def __init__(
        self,
        obj: t.Union['RenderableObject', 'NamedVariable'],
        guide_lines: bool = False,
    ) -> None:
        self._color = 'default'
        self._style = ''
        self._objs = []
        for line in self._expand_lines(obj._origin, indent=2):
            self._objs.append(RenderableObject(line))
            self._objs.append(LineBreak())
        if isinstance(obj, NamedVariable):
            self._objs[0] = NamedVariable(
                obj._name,
                self._objs[0]._origin.lstrip(),  # type: ignore
                _quote_string=False,
            )
            self._objs.insert(0, Space(2))

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return ''.join(
            x.render(color_code_scheme=color_code_scheme) for x in self._objs
        )

    def _expand_lines(self, element: t.Any, indent: int = 0) -> t.Iterator[str]:
        def wrap(text: str) -> str:
            return ' ' * indent + text

        if element:
            if isinstance(element, dict):
                yield wrap('{')
                for k, v in element.items():
                    v2 = tuple(self._expand_lines(v, indent + 4))
                    if len(v2) == 0:
                        raise Exception
                    elif len(v2) == 1:
                        v3 = v2[0].lstrip() + ','
                    else:
                        v3 = '(\n{}\n{}),'.format(
                            '\n'.join(v2), ' ' * (indent + 2)
                        )
                    yield '{}{}: {}'.format(
                        ' ' * (indent + 2),
                        '"{}"'.format(k) if isinstance(k, str) else str(k),
                        v3,
                    )
                yield wrap('}')
            elif isinstance(element, list):
                yield wrap('[')
                for each in element:
                    for x in self._expand_lines(each, indent + 2):
                        yield x + ','
                yield wrap(']')
            elif isinstance(element, str):
                yield wrap(self._quote_string(element))
            elif isinstance(element, tuple):
                yield wrap('(')
                for each in element:
                    for x in self._expand_lines(each, indent + 2):
                        yield x + ','
                yield wrap(')')
            elif isinstance(element, (set, frozenset)):
                yield wrap('{')
                for each in sorted(element):
                    for x in self._expand_lines(each, indent + 2):
                        yield x + ','
                yield wrap('}')
            else:
                text = str(element)
                if '\n' in text:
                    yield textwrap.indent(text, ' ' * indent)
                else:
                    yield wrap(text)
        else:
            yield wrap(
                self._quote_string(element)
                if isinstance(element, str)
                else str(element)
            )

    def _quote_string(self, s: str) -> str:
        return NamedVariable.quote_string(s)


class ExpandedObjectGroup(TextObjectGroup):
    def __init__(
        self,
        body_parts: t.Sequence[TextObject],
        before_body_parts: t.Sequence[TextObject],
    ) -> None:
        self._objs = [LineBreak()]
        i = 0
        while i < len(body_parts):
            element = body_parts[i]
            if isinstance(element, InBodySeparator):
                self._objs.append(element)
                self._objs.append(LineBreak())
                i += 2
            else:
                self._objs.append(element)
                i += 1

        can_be_single_line = True
        available_space = console.width - sum(len(x) for x in before_body_parts)
        for x in self._objs:
            for _ in x.render(color_code_scheme='none'):
                available_space -= 1
                if available_space < 0:
                    can_be_single_line = False
                    break
            if not can_be_single_line:
                break
        self._single_line = can_be_single_line

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        out = ''.join(
            x.render(color_code_scheme=color_code_scheme)
            for x in self._objs
        )
        if self._single_line:
            out = out.replace('\n', ' ')
        return out


FuncnameSeparator = BodySeparator


class InBodySeparator(TextObject):
    def __init__(self, char: str = ';') -> None:
        self._sep = char

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render(
            (self._sep, self.color, 'dim'), code_scheme=color_code_scheme
        )


class Index(TextObject):
    def __init__(self, index: int) -> None:
        self._text = '[{}]'.format(index)
        self.editable = False

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render((self._text, 'red'), code_scheme=color_code_scheme)


class LineBreak(TextObject):
    def __init__(self, count: int = 1) -> None:
        self._count = count
        self.editable = False

    def render(self, **_) -> str:
        return '\n' * self._count


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

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
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
            (self._name + ' = ', color1, 'dim'),
            (self._value, color2, self.style),
            code_scheme=color_code_scheme,
        )

    @staticmethod
    def quote_string(s: str) -> str:
        if s and s[0] == '"':
            return s
        else:
            return '"' + s.replace('"', '\\"') + '"'


class RenderableObject(TextObject):
    def __init__(
        self, obj: t.Any, color: T.Color = 'default', style: T.Style = ''
    ) -> None:
        self._origin = obj
        self._text = str(obj)
        self.color = color
        self.style = style

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        color = self.color
        if color == 'default':
            if self._origin is True:
                color = 'green'
            elif self._origin is False:
                color = 'red'
            elif self._origin is None:
                color = 'magenta'
        return render(
            (self._text, color, self.style), code_scheme=color_code_scheme
        )


class RichObject(TextObject):
    def __init__(self, obj: t.Any) -> None:
        self._obj = obj

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str: ...


class Source(TextObject):
    def __init__(self, frame: FrameInfo) -> None:
        self._fname = frame.file_name
        self._pname = '[{}]'.format(frame.package_name)
        self._path = frame.file_path
        self._lineno = self._pad_lineno(frame.line_number)

    def render(
        self,
        name_format='filename:lineno',
        external_name_format='[libname]:filename:lineno',
        color_code_scheme: T.CodeScheme = 'none',
    ) -> str:
        """
        name_style:
            'filename': e.g. 'main.py'
            'relpath': e.g. 'example/main.py'
        name_style_for_external_lib:
            'follow_name_style': follow `name_style` value.
            'libname_relpath': show `[{libname}]/{relpath}:{lineno}`
            'libname_filename': show `[{libname}]/{filename}:{lineno}`
        shrink_relpath_with_separator:
            '~': show `[{libname}]/~/{filename}:{lineno}`.
                e.g. "[lk_utils]/~/promise.py:10".
            '~x': show `[{libname}]/~{level_count}/{filename}:{lineno}`.
                e.g. "[lk_utils]/~1/promise.py:10".
            '...': show `[{libname}]/.../{filename}:{lineno}`.
                e.g. "[lk_utils]/.../promise.py:10".
            '...x': show `[{libname}]/...{level_count}/{filename}:{lineno}`.
                e.g. "[lk_utils]/...1/promise.py:10".
        """
        # TODO
        assert name_format == 'filename:lineno'
        assert external_name_format == '[libname]:filename:lineno'
        if path_glob.is_external_path(self._path):
            return render(
                (self._pname, 'magenta'),
                (':', 'blue'),
                (self._fname, 'blue'),
                (':', 'blue', 'dim'),
                (self._lineno, 'blue', 'dim'),
                code_scheme=color_code_scheme,
            )
        else:
            return render(
                (self._fname, 'blue'),
                (':', 'blue', 'dim'),
                (self._lineno, 'blue', 'dim'),
                code_scheme=color_code_scheme,
            )

    def _pad_lineno(self, number: int, width: int = 3) -> str:
        a, b = divmod(len(str(number)), width)
        return str(number).ljust(width * (a + (1 if b else 0)))


class Space(TextObject):
    def __init__(self, length: int = 1) -> None:
        self._length = length
        self.editable = False

    def render(self, **_) -> str:
        return ' ' * self._length


class SpecialExpandedObject(TextObject):
    @classmethod
    def check_expandable(cls, obj: TextObject) -> bool:
        if isinstance(obj, (RenderableObject, NamedVariable)):
            origin = obj._origin
            if isinstance(origin, str):
                return True
            elif isinstance(origin, dict):
                if len(origin) > 1 and all(
                    (isinstance(k, str) for k in origin.keys())
                ):
                    return True
            elif isinstance(origin, (list, tuple)):
                if (
                    len(origin) > 1
                    and all(
                        (
                            (
                                isinstance(x, (list, tuple))
                                and len(x) > 0
                                and all(
                                    (
                                        isinstance(y, (str, int, float, bool))
                                        for y in x
                                    )
                                )
                            )
                            for x in origin
                        )
                    )
                    and all((isinstance(x, str) for x in origin[0]))
                    and len(origin[0]) > max((len(x) for x in origin[1:]))
                ):
                    return True
        return False

    def __init__(
        self, obj: t.Union['RenderableObject', 'NamedVariable']
    ) -> None:
        self._data = []
        origin = obj._origin
        if isinstance(origin, str):
            if m := re.fullmatch(r'(\w+:) (\w+) -> (\w+)', origin):
                if m.group(1):
                    self._data.append(RenderableObject(m.group(1)))
                    self._data.append(Space())
                self._data.append(RenderableObject(m.group(2), color='red'))
                self._data.append(Space())
                self._data.append(RenderableObject('->'))
                self._data.append(Space())
                self._data.append(RenderableObject(m.group(3), color='green'))
            else:
                ...
