from inspect import currentframe
from typing import Any, Dict

from . import console
from .config import config
from .formatter import formatter
from .frame_info import FrameInfo, from_frame
from .markup import MarkupParser, ParsedMarks


class Counter:
    _global_index: int = 0
    _scoped_indexes: Dict[str, int] = {}
    _line_indexes: Dict[str, int] = {}
    _scope_stack: list = []

    def reset_all(self) -> None:
        self._global_index = 0
        self._scoped_indexes.clear()
        self._line_indexes.clear()

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

    def update_line(self, line_key: str) -> int:
        if line_key not in self._line_indexes:
            self._line_indexes[line_key] = 0
        self._line_indexes[line_key] += 1
        return self._line_indexes[line_key]

    def get_line(self, line_key: str) -> int:
        return self._line_indexes.get(line_key, 0)

    def push_scope(self, scope_id: str) -> None:
        self._scope_stack.append(scope_id)

    def pop_scope(self) -> None:
        if self._scope_stack:
            self._scope_stack.pop()

    def get_current_scope(self) -> str:
        return self._scope_stack[-1] if self._scope_stack else None


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

    if args and isinstance(args[0], str) and args[0].startswith(':'):
        markup_str = args[0]
        args = args[1:]
    elif args and isinstance(args[-1], str) and args[-1].startswith(':') and _parser.is_valid_markup(args[-1]):
        markup_str = args[-1]
        args = args[:-1]

    marks = _parser.parse(markup_str) if markup_str else ParsedMarks()

    if marks.parent is not None and marks.parent > 0:
        frame = _get_caller_frame(extra_levels + marks.parent)
    else:
        frame = _get_caller_frame(extra_levels)

    color_level = marks.color if marks.color is not None else marks.verbosity

    index_value = None
    show_index = False
    reset_only = False
    if marks.index is not None:
        show_index = True
        if marks.index == 0:
            counter.reset_all()
            index_value = None
            show_index = False
            reset_only = True
        elif marks.index == 1:
            line_key = f"{frame.filepath}:{frame.lineno}"
            index_value = counter.update_line(line_key)
        elif marks.index == 2:
            current_scope = counter.get_current_scope()
            if current_scope:
                scope_id = current_scope
            else:
                scope_id = frame.funcname
            index_value = counter.update_scoped(scope_id)
        elif marks.index == 3:
            index_value = counter.update_global()

    if marks.divider is not None:
        from .console import get_console_width

        width = get_console_width() - 4
        divider = formatter.format_divider('-', width)
        console.print(divider)

    if marks.verbosity is not None and args:
        from .sourcemap import get_varnames_from_call

        varnames = get_varnames_from_call(frame.filepath, frame.lineno, 'np.show')
        if not varnames:
            varnames = get_varnames_from_call(frame.filepath, frame.lineno, 'show')
        frame.varnames = varnames if varnames else ()

    message = formatter.format_message(
        args=args,
        frame=frame,
        marks=marks,
        show_source=config.show_source,
        show_funcname=config.show_funcname,
        show_varnames=config.show_varnames or (marks.verbosity is not None),
        show_index=show_index,
        color_level=color_level if color_level is not None else 0,
        index_value=index_value,
    )

    if marks.rich is not None:
        message = formatter.apply_rich_markup(message)

    if not args:
        return

    console.print(message)


_parser = MarkupParser()
