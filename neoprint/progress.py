import typing as t
from typing import Literal

from .console import (
    debugger,
    get_console_width,
    print,
    AnsiColor,
)
from .format import format_list
from .frame_info import get_caller_frame
from .util import strip_ansi
from .markup import MarkupParser, ParsedMarks
from .text_object import (
    BodyPart,
    BodySeparator,
    Space,
    ProgressBar,
    Indicator,
)


class Progress:
    _SPINNER_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    _MARKUP_PARSER = MarkupParser()

    def __init__(
        self,
        total: t.Optional[int] = None,
        indicator_style: Literal[
            'counter', 'digital', 'decimal', 'none'
        ] = 'counter',
    ) -> None:
        self._total = total
        self.index = 0
        self.indicator_style = indicator_style
        self._type_determined = False
        self._is_spinner = False
        self._spinner_index = 0

    @property
    def total(self) -> t.Optional[int]:
        return self._total

    @total.setter
    def total(self, value: t.Optional[int]) -> None:
        if self._type_determined:
            raise ValueError(
                'Cannot set total after update() has been called '
                'and progress type has been determined.'
            )
        self._total = value

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        if not self._type_determined:
            self._type_determined = True
            self._is_spinner = self._total is None

        self.index += 1
        if self._is_spinner:
            self._spinner_index += 1

        markup_str = kwargs.pop('markup', '')

        if args and isinstance(args[0], str) and args[0].startswith(':'):
            markup_str = args[0]
            args = args[1:]
        elif (
            args
            and isinstance(args[-1], str)
            and args[-1].startswith(':')
            and self._MARKUP_PARSER.is_valid_markup(args[-1])
        ):
            markup_str = args[-1]
            args = args[:-1]

        marks = (
            self._MARKUP_PARSER.parse(markup_str)
            if markup_str
            else ParsedMarks()
        )

        line = self._render(args, marks, markup_str)

        end = '\n' if debugger.enabled else '\r'
        print(line, end=end, flush=True)

    def _render(
        self, args: t.Tuple, marks: ParsedMarks, markup_str: str
    ) -> str:
        extra_levels = marks.parent if marks.parent is not None else 0
        frame = get_caller_frame(extra_levels=1 + extra_levels)

        texts = format_list(
            *args,
            markup=markup_str,
            _caller_filepath=frame.filepath if frame else None,
            _caller_lineno=frame.lineno if frame else None,
            _caller_funcname=frame.funcname if frame else None,
            _extra_levels=0,
        )

        body_sep_index = None
        for i, text_obj in enumerate(texts):
            if isinstance(text_obj, BodySeparator):
                body_sep_index = i
                break

        if body_sep_index is not None:
            if self._is_spinner:
                spinner_char = self._SPINNER_CHARS[
                    self._spinner_index % len(self._SPINNER_CHARS)
                ]
                spinner_obj = BodyPart(spinner_char, color=AnsiColor.RED)
                texts.insert(body_sep_index + 1, spinner_obj)
                texts.insert(body_sep_index + 2, Space())
            else:
                bar_obj = ProgressBar(
                    self.index, self._total, color=AnsiColor.RED
                )
                indicator_obj = Indicator(
                    self.index,
                    self._total,
                    style=self.indicator_style,
                    color=AnsiColor.RED,
                )
                texts.insert(body_sep_index + 1, bar_obj)
                texts.insert(body_sep_index + 2, indicator_obj)
                texts.insert(body_sep_index + 3, Space())

        output = ''.join(t.render('ansi') for t in texts)

        if not debugger.enabled:
            console_width = get_console_width()
            stripped_length = len(strip_ansi(output))
            if stripped_length > console_width:
                excess = stripped_length - console_width + 3
                output = output[:-excess] + '...'

        return output

    def __enter__(self) -> 'Progress':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not debugger.enabled:
            print()  # 添加换行，确保进度条后有新的一行
