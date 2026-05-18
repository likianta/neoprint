from inspect import currentframe
from typing import Any, Dict

from . import console
from .config import config
from .formatter import formatter
from .frame_info import FrameInfo, from_frame
from .markup import MarkupParser


class Counter:
    _global_index: int = 0
    _scoped_indexes: Dict[str, int] = {}

    def reset_all(self) -> None:
        self._global_index = 0
        self._scoped_indexes.clear()

    def update_global(self) -> int:
        self._global_index += 1
        return self._global_index

    def update_scoped(self, scope_id: str) -> int:
        if scope_id not in self._scoped_indexes:
            self._scoped_indexes[scope_id] = 0
        self._scoped_indexes[scope_id] += 1
        return self._scoped_indexes[scope_id]

    def get_scoped(self, scope_id: str) -> int:
        return self._scoped_indexes.get(scope_id, 0)


counter = Counter()


def _get_caller_frame(extra_levels: int = 0) -> FrameInfo:
    frame = currentframe()
    if frame is None:
        return FrameInfo('<unknown>', 0, '<unknown>')
    levels = 2 + extra_levels
    for _ in range(levels):
        frame = frame.f_back
        if frame is None:
            return FrameInfo('<unknown>', 0, '<unknown>')
    return from_frame(frame)


def show(*args: Any, **kwargs: Any) -> None:
    extra_levels = kwargs.pop('_extra_levels', 0)
    markup_str = kwargs.pop('markup', '')
    if (
        markup_str
        and markup_str.startswith(':')
        and _parser.is_valid_markup(markup_str)
    ):
        args = args + (markup_str,) if len(args) > 0 else (markup_str,)

    raw_args, markup_pos, marks = _parser.extract_from_args(args)

    if marks.parent is not None and marks.parent > 0:
        frame = _get_caller_frame(extra_levels + marks.parent)
    else:
        frame = _get_caller_frame(extra_levels)

    color_level = marks.color if marks.color is not None else marks.verbosity

    index_value = None
    show_index = False
    if marks.index is not None:
        show_index = True
        if marks.index == 0:
            counter.reset_all()
            return
        elif marks.index == 1:
            index_value = counter.update_scoped(frame.id)
        elif marks.index == 2:
            index_value = counter.update_global()
        else:
            index_value = counter.update_global()

    message = formatter.format_message(
        args=raw_args,
        frame=frame,
        marks=marks,
        show_source=config.show_source,
        show_funcname=config.show_funcname,
        show_varnames=config.show_varnames,
        show_index=show_index,
        color_level=color_level if color_level is not None else 0,
        index_value=index_value,
    )

    if marks.divider is not None:
        from .console import get_console_width

        width = get_console_width() - 4
        divider = formatter.format_divider('-', width)
        console.print(divider)

    if marks.rich is not None:
        message = formatter.apply_rich_markup(message)

    console.print(message)


_parser = MarkupParser()
