import re
import rich.box
import rich.jupyter
import rich.markdown
import rich.table
import rich.text
import textwrap
import typing as t
from functools import cache
from types import FunctionType
from .config import config
from .console import console
from .console import dprint  # noqa
from .console import legacy_rich_console
from .console import rich_console
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

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return ''.join(
            x.render(color_code_scheme=color_code_scheme) for x in self._objs
        )


# ------------------------------------------------------------------------------


class BodySeparator(TextObject):
    def __init__(self, char: str = '|') -> None:
        self._char = char

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render(
            (self._char, 'default', 'dim'), code_scheme=color_code_scheme
        )


class DividerLine(TextObjectGroup):
    def __init__(
        self,
        body_parts: t.Sequence[TextObject],
        non_body_parts: t.Sequence[TextObject],
        bold: bool = False,
    ) -> None:
        super().__init__()
        self._div_char = '█' if bold else '─'

        body_space = console.width - sum(map(len, non_body_parts))
        if body_parts:
            spare_space = body_space - sum(map(len, body_parts)) - 2
            #   `-2` for space around `body_parts`.
            assert spare_space >= 2
            #   spare_space should be at least 2 -- one for the left part of
            #   divchar, another for the right.
            left_part_space = spare_space // 2
            right_part_space = (
                left_part_space if spare_space % 2 == 0 else left_part_space + 1
            )
            self._objs.extend(
                (
                    Text(self._div_char * left_part_space),
                    Space(),
                    *body_parts,
                    Space(),
                    Text(self._div_char * right_part_space),
                )
            )
        else:
            assert body_space > 0
            self._objs.append(Text(self._div_char * body_space, style='dim'))

        self._full_dimmed_line = not body_parts

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        if self._full_dimmed_line:
            assert len(self._objs) == 1
            self._objs[0].style = 'dim'  # make sure the line is dimmed.
            return self._objs[0].render(color_code_scheme=color_code_scheme)
        else:
            return super().render(color_code_scheme=color_code_scheme)


class ExpandedObjectGroup(TextObjectGroup):
    def __init__(
        self,
        body_parts: t.Sequence[TextObject],
        non_body_parts: t.Sequence[TextObject],
    ) -> None:
        super().__init__()
        self._objs.append(LineBreak())
        i = 0
        while i < len(body_parts):
            element = body_parts[i]
            if isinstance(element, InBodySeparator):
                self._objs.append(element)
                self._objs.append(LineBreak())
                i += 2
            elif isinstance(element, SpecialExpandedObject):
                self._objs.append(element)
                if i + 1 < len(body_parts):
                    assert isinstance(body_parts[i + 1], InBodySeparator)
                    assert isinstance(body_parts[i + 2], Space)
                    # self._objs.append(Space())
                    self._objs.append(LineBreak())
                    i += 3
                else:
                    i += 1
            else:
                self._objs.append(element)
                i += 1

        can_be_single_line = True
        available_space = console.width - sum(len(x) for x in non_body_parts)
        for x in self._objs[1:]:
            if isinstance(x, ExpandedObject):
                text = x.render(color_code_scheme='none', compact=True)
            else:
                text = x.render(color_code_scheme='none')
            available_space -= len(text)
            if available_space <= 0:
                can_be_single_line = False
                break
        self._single_line = can_be_single_line

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        if self._single_line:
            return ''.join(
                (
                    ''
                    if isinstance(x, LineBreak)
                    else x.render(
                        color_code_scheme=color_code_scheme, compact=True
                    )
                    if isinstance(x, (ExpandedObject, SpecialExpandedObject))
                    else x.render(color_code_scheme=color_code_scheme)
                    for x in self._objs[1:]
                )
            )
        else:
            return ''.join(
                x.render(color_code_scheme=color_code_scheme)
                for x in self._objs
            )


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


class RichObject(TextObject):
    def __init__(self, obj: rich.jupyter.JupyterMixin) -> None:
        self._obj = obj
        self.editable = False

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        # https://chatgpt.com/share/6a16a585-0e00-8320-97ee-5fc2b572690e
        if color_code_scheme == 'none':
            return legacy_rich_console.capture_output(self._obj).rstrip()
        elif color_code_scheme == 'ansi':
            return rich_console.capture_output(self._obj).rstrip()
        else:
            raise NotImplementedError


class Source(TextObject):
    def __init__(self, frame: FrameInfo) -> None:
        self._path = frame.file_path
        self._pname = '[{}]'.format(frame.package_name)
        self._fname = frame.file_name
        if config.sourcemap_alignment == 'left':
            self._lineno = self._pad_lineno(frame.line_number)
        else:
            self._lineno = str(frame.line_number)

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
                (':', 'blue', 'dim'),
                (self._fname, 'blue'),
                (':', 'green', 'dim'),
                (self._lineno, 'green'),
                code_scheme=color_code_scheme,
            )
        else:
            return render(
                (self._fname, 'blue'),
                (':', 'green', 'dim'),
                (self._lineno, 'green'),
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


class SpecialExpandedObject(TextObjectGroup):
    _form_type: t.Literal['transform', 'kv_table', 'table']

    @classmethod
    def check_expandable(cls, obj: TextObject) -> bool:
        if isinstance(obj, (Text, NamedVariable)):
            origin = obj._origin
            if isinstance(origin, str):
                return bool(re.fullmatch(r'(?:[^:]+: )?.*? -> .+', origin))
            elif isinstance(origin, dict):
                if len(origin) > 1 and all(
                    (isinstance(k, str) for k in origin.keys())
                ):
                    return True
            elif isinstance(origin, (list, tuple)):
                # table spec:
                # - the form is `Sequence[header_row, *body_rows]`
                # - header_row is a sequence of strings
                # - body_rows are sequences of strings, ints, floats, or bools
                # - header_row length >= the longest body_row length
                if (
                    len(origin) >= 2
                    and all(
                        (
                            (
                                isinstance(row, (list, tuple))
                                and len(row) > 0
                                and all(
                                    (
                                        isinstance(
                                            cell, (str, int, float, bool)
                                        )
                                        for cell in row
                                    )
                                )
                            )
                            for row in origin
                        )
                    )
                    and all(
                        (isinstance(head_cell, str) for head_cell in origin[0])
                    )
                    and len(origin[0]) >= max((len(row) for row in origin[1:]))
                ):
                    return True
        return False

    def __init__(self, obj: t.Union['Text', 'NamedVariable']) -> None:
        super().__init__()
        origin = obj._origin
        if isinstance(origin, str):
            self._form_type = 'transform'
            a, b, c = ('', *origin.split(' -> '))
            if ':' in b:
                a, b = b.split(':', 1)
            if a:
                self._objs.append(Text(a + ': '))
            assert b
            self._objs.append(Text(b, color='red'))
            self._objs[-1].editable = False
            self._objs.append(Space())
            self._objs.append(Text('->'))
            self._objs.append(Space())
            assert c
            self._objs.append(Text(c, color='green'))
            self._objs[-1].editable = False
        elif isinstance(origin, dict):  # kv table
            self._form_type = 'kv_table'
            table = rich.table.Table(
                'KEY', 'VALUE', header_style='yellow', box=rich.box.ROUNDED
            )
            for k, v in origin.items():
                table.add_row(str(k), str(v))
            self._objs.append(RichObject(table))
        else:  # isinstance(origin, (list, tuple))
            self._form_type = 'table'
            table = None
            for i, row in enumerate(origin):
                if i == 0:
                    table = rich.table.Table(
                        *row, header_style='yellow', box=rich.box.ROUNDED
                    )
                else:
                    table.add_row(*map(str, row))  # type: ignore
            assert table
            self._objs.append(RichObject(table))

    def render(
        self, color_code_scheme: T.CodeScheme = 'none', compact: bool = False
    ) -> str:
        if compact:
            if self._form_type == 'transform':
                return super().render(color_code_scheme)
            else:
                assert len(self._objs) == 1
                return self._objs[0].render(color_code_scheme)
        else:
            indent = config.multiline_indent
            if self._form_type == 'transform':
                return ' ' * indent + super().render(color_code_scheme)
            else:
                return textwrap.indent(
                    self._objs[0].render(color_code_scheme), ' ' * indent
                )


class Text(TextObject):
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


# ------------------------------------------------------------------------------


class ExpandedObject(TextObjectGroup):
    class Indent(Space):
        def __init__(self, level: int) -> None:
            super().__init__(level * config.multiline_indent)

    class OptionalText(Text):
        pass

    class Separator(TextObject):
        def render(
            self,
            compact: bool = False,
            color_code_scheme: T.CodeScheme = 'none',
        ) -> str:
            return render(
                (';', self.color, 'dim'),
                (' ' if compact else '\n',),
                code_scheme=color_code_scheme,
            )

    @classmethod
    def check_expandable(cls, obj: TextObject) -> bool:
        return isinstance(obj, (Text, NamedVariable))

    def __init__(self, obj: t.Union['Text', 'NamedVariable']) -> None:
        super().__init__()
        self._origin = obj._origin

        self._comma = Text(',')
        self._line_break = LineBreak()
        self._sep = ExpandedObject.Separator()

        self._objs.extend(self._expand_lines(obj._origin, 1))
        self._objs.pop()  # remove last LineBreak
        if isinstance(obj, NamedVariable):
            self._objs[1] = NamedVariable(
                obj._name,
                self._objs[1]._origin,  # type: ignore
                _quote_string=False,
            )

    def render(
        self, color_code_scheme: T.CodeScheme = 'none', compact: bool = False
    ) -> str:
        if compact:
            x = self._pretty_format(self._origin)
            if x.editable:
                x.color = self._color
                x.style = self._style
            return x.render(color_code_scheme=color_code_scheme)
        else:
            return super().render(color_code_scheme=color_code_scheme)

    # def render_compact(self, color_code_scheme: T.CodeScheme = 'none') -> str:
    #     return (
    #         ''.join(
    #             (
    #                 ''
    #                 if x is self._line_break
    #                 or isinstance(
    #                     x, (ExpandedObject.Indent, ExpandedObject.OptionalText)
    #                 )
    #                 else x.render(
    #                     compact=True, color_code_scheme=color_code_scheme
    #                 )
    #                 if x is self._sep
    #                 else x.render(color_code_scheme=color_code_scheme)
    #                 for x in self._objs
    #             )
    #         )
    #         .replace(',)', ')')
    #         .replace(',]', ']')
    #         .replace(',}', '}')
    #     )

    def _expand_lines(
        self, element: t.Any, _level: int = 0
    ) -> t.Iterator[TextObject]:
        def row(*args):
            yield self._indent(_level)
            yield from args
            yield self._line_break

        if element is None:
            yield from row(Text('None', 'magenta'))
        elif isinstance(element, FunctionType):
            yield from row(Text('<function {}>'.format(element.__name__)))
        elif isinstance(element, bool):
            yield from row(Text(str(element), 'green' if element else 'red'))
        elif isinstance(element, str):
            yield from row(Text(self._quote_string(element)))
        elif isinstance(element, (dict, frozenset, list, set, tuple)):
            if element:
                if isinstance(element, dict):
                    yield from row(Text('{'))
                    for k, v in element.items():
                        yield self._indent(_level + 1)
                        yield Text(self._quote_string(k))
                        yield Text(': ')

                        v2 = tuple(self._expand_lines(v, _level + 1))
                        #   Tuple[_Indent, TextObject, ..., LineBreak]
                        if len(v2) == 0 or len(v2) == 1:
                            raise Exception
                        if v2[1]._origin in ('(', '[', '{'):  # type: ignore
                            yield from v2[1:-1]
                            yield self._comma
                            yield ExpandedObject.OptionalText(' ')
                            yield self._line_break
                        else:
                            if (
                                len(v2) == 3 and '\n' not in v2[1]._origin  # type: ignore
                            ):
                                yield v2[1]
                                yield self._comma
                                yield ExpandedObject.OptionalText(' ')
                                yield self._line_break
                            else:
                                yield ExpandedObject.OptionalText('(')
                                yield self._line_break
                                yield from v2
                                yield from row(
                                    ExpandedObject.OptionalText('),')
                                )
                    yield from row(Text('}'))
                else:
                    yield from row(
                        Text(
                            '['
                            if isinstance(element, list)
                            else '('
                            if isinstance(element, tuple)
                            else '{'
                        )
                    )
                    for each in element:
                        x = tuple(self._expand_lines(each, _level + 1))
                        #   Tuple[_Indent, TextObject, ..., LineBreak]
                        yield from x[:-1]
                        yield self._comma
                        yield ExpandedObject.OptionalText(' ')
                        yield x[-1]
                    yield from row(
                        Text(
                            ']'
                            if isinstance(element, list)
                            else ')'
                            if isinstance(element, tuple)
                            else '}'
                        )
                    )
            else:
                yield from row(Text(str(element)))
        elif isinstance(element, (float, int)):
            yield from row(Text(str(element)))
        else:  # it's an object!
            # ref: `[lib]objprint/objprint.py:ObjPrint:_objstr`.
            if element.__class__.__str__ is object.__str__:
                yield from row(
                    Text(
                        '<{} id={}>'.format(
                            element.__class__.__name__, id(element)
                        )
                    )
                )
            else:
                text = str(element)
                yield from row(
                    Text(
                        textwrap.indent(text, ' ' * _level)
                        if '\n' in text
                        else text
                    )
                )

    @cache
    def _indent(self, level: int) -> Indent:
        return ExpandedObject.Indent(level)

    def _pretty_format(self, element: t.Any) -> TextObject:
        """
        a "single-line" version of `_expand_lines`.
        """
        if element is None:
            return Text('None', 'magenta')
        elif isinstance(element, FunctionType):
            return Text('<function {}>'.format(element.__name__))
        elif isinstance(element, bool):
            return Text(str(element), 'green' if element else 'red')
        elif isinstance(element, str):
            return Text(self._quote_string(element))
        elif isinstance(
            element, (dict, float, frozenset, int, list, set, tuple)
        ):
            return Text(str(element))
        else:  # an object
            # ref: `[lib]objprint/objprint.py:ObjPrint:_objstr`.
            if element.__class__.__str__ is object.__str__:
                return Text(
                    '<{} id={}>'.format(element.__class__.__name__, id(element))
                )
            else:
                text = str(element)
                return Text(
                    textwrap.dedent(text).replace('\n', ' ')
                    if '\n' in text
                    else text
                )

    def _quote_string(self, s: t.Any) -> str:
        return NamedVariable.quote_string(s) if isinstance(s, str) else str(s)


class Markdown(RichObject):
    def __init__(self, text: str) -> None:
        super().__init__(rich.markdown.Markdown(textwrap.dedent(text)))
