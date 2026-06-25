import re
import textwrap
import textwrap as tw
import typing as t
from functools import cache
from types import FunctionType

import rich.box
import rich.jupyter
import rich.markdown
import rich.table
import rich.text

from .base import T
from .base import TextObject
from .base import TextObjectGroup
from .invisible import LineBreak
from .invisible import Space
from .named_variable import NamedVariable
from .rich import RichObject
from .separator import InBodySeparator
from .text import Text
from ..config import config
from ..console import console
from ..render import render


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
            color_code_scheme: T.ColorCodeScheme = 'plain',
        ) -> str:
            return render(
                (';', self.color, 'dim'),
                (' ' if compact else '\n',),
                color_code_scheme=color_code_scheme,
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
        self,
        color_code_scheme: T.ColorCodeScheme = 'plain',
        compact: bool = False,
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
                text = x.render(color_code_scheme='plain', compact=True)
            else:
                text = x.render(color_code_scheme='none')
            available_space -= len(text)
            if available_space <= 0:
                can_be_single_line = False
                break
        self._single_line = can_be_single_line

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
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
        self,
        color_code_scheme: T.ColorCodeScheme = 'plain',
        compact: bool = False,
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
                return tw.indent(
                    self._objs[0].render(color_code_scheme), ' ' * indent
                )
