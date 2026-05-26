import typing as t
from .console import console
from .frame_info import FrameInfo
from .path_glob import path_glob
from .render import T
from .render import render


class TextObject:
    color: T.Color = 'default'
    # color: t.Union[t.Literal[''], T.Color] = ''
    editable: bool = True  # do `color` and `style` post editable.
    style: T.Style = ''

    def __len__(self) -> int:
        return len(self.render(color_code_scheme='none'))

    def render(self, *_, **__) -> str:
        raise NotImplementedError


class BodySeparator(TextObject):
    def __init__(self, char: str = '|') -> None:
        self._char = char

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render(
            (self._char, 'default', 'dim'),
            code_scheme=color_code_scheme,
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


FuncnameSeparator = BodySeparator


class InBodySeparator(TextObject):
    def __init__(self, char: str = ';') -> None:
        self._sep = char

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render(
            (self._sep, self.color, 'dim'),
            code_scheme=color_code_scheme,
        )


class Index(TextObject):
    def __init__(self, index: int) -> None:
        self._text = '[{}]'.format(index)
        self.editable = False

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render((self._text, 'red'), code_scheme=color_code_scheme)


class NamedVariable(TextObject):
    def __init__(
        self,
        name: str,
        value: t.Any,
        color: T.Color = 'default',
        style: T.Style = '',
    ) -> None:
        self._name = name
        self._value = str(value)
        self.color = color
        self.style = style

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render(
            (self._name + ' = ', self.color, 'dim'),
            (self._value, self.color, self.style),
            code_scheme=color_code_scheme,
        )


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
    def __init__(self, size: int = 1) -> None:
        self._size = size

    def render(self, **_) -> str:
        return ' ' * self._size


class Text(TextObject):
    def __init__(self, obj: t.Any) -> None:
        self._text = str(obj)

    def render(self, color_code_scheme: T.CodeScheme = 'none') -> str:
        return render(
            (self._text, self.color, self.style)
            if self.style
            else (self._text, self.color),
            code_scheme=color_code_scheme,
        )
