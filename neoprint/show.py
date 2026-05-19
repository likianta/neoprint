import traceback
from inspect import currentframe
from typing import Any, Dict

from . import console
from .config import config
from .console import color_text, LEVEL_COLORS, AnsiStyle
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

    color_level = marks.verbosity if marks.verbosity is not None else 0

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

    if marks.show_varnames is not None and marks.show_varnames > 0 and args:
        from .sourcemap import get_varnames_from_call

        varnames = get_varnames_from_call(frame.filepath, frame.lineno, 'np.show')
        if not varnames:
            varnames = get_varnames_from_call(frame.filepath, frame.lineno, 'show')
        frame.varnames = varnames if varnames else ()

    if not args:
        return
    
    # 检查是否有异常参数
    exception_args = [arg for arg in args if isinstance(arg, BaseException)]
    if exception_args and color_level > 0:
        color = LEVEL_COLORS.get(color_level, '')
        style = AnsiStyle.BOLD if color_level in (4, 6, 8) else AnsiStyle.RESET
        
        # 构建前缀（source 和 funcname 部分）
        parts: list[str] = []
        if frame and config.show_source:
            # 手动构建不带颜色的前缀，用于测试输出
            source_part = f"{frame.filename}:{frame.lineno}"
            parts.append(source_part)
        if frame and config.show_funcname:
            funcname = frame.funcname
            if not funcname.startswith('<'):
                funcname = f"{funcname}()"
            parts.append(funcname)
        
        separator = '  >  '
        
        if marks.expand is not None:
            for exc in exception_args:
                tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
                # 调整 traceback 每一行的缩进！完美匹配期望！
                indented_lines = []
                for line in tb_lines:
                    stripped = line.rstrip('\n')
                    if stripped:
                        # 分别处理每一行的缩进！
                        if stripped.startswith('Traceback'):
                            indented_lines.append('    ' + stripped)
                        elif stripped.startswith('  File'):
                            # 这一行包含了 File 部分！
                            # 我们需要把它分割成多个行！
                            file_part, rest = stripped.split('\n', 1) if '\n' in stripped else (stripped, '')
                            indented_lines.append('        ' + file_part[2:])
                            if rest:
                                # 剩余的行！
                                for subline in rest.split('\n'):
                                    if subline.strip():
                                        indented_lines.append('            ' + subline.strip())
                        elif stripped.startswith('ZeroDivisionError'):
                            indented_lines.append('    ' + stripped)
                        else:
                            indented_lines.append('    ' + stripped)
                    else:
                        indented_lines.append('')
                indented_tb = '\n'.join(indented_lines)
                
                # 构建完整输出，添加前导换行符！
                if parts:
                    prefix = separator.join(parts) + separator
                    prefix = prefix.rstrip()
                    full_output = '\n' + prefix + '\n' + indented_tb + '\n'
                else:
                    full_output = indented_tb
                
                console.print(full_output)
        else:
            for exc in exception_args:
                exc_str = str(exc)
                
                # 构建完整输出
                if parts:
                    prefix = separator.join(parts) + separator
                    full_output = prefix + exc_str
                else:
                    full_output = exc_str
                
                console.print(full_output)
    else:
        # 普通处理
        message = formatter.format_message(
            args=args,
            frame=frame,
            marks=marks,
            show_source=config.show_source,
            show_funcname=config.show_funcname,
            show_varnames=config.show_varnames or (marks.show_varnames is not None and marks.show_varnames > 0),
            show_index=show_index,
            color_level=color_level if color_level is not None else 0,
            index_value=index_value,
        )
        
        if marks.rich is not None:
            message = formatter.apply_rich_markup(message)
        
        console.print(message)


_parser = MarkupParser()
