import ast
import os
import typing as tp

from .console import dprint  # noqa


class VarnamesAnalyzer(ast.NodeVisitor):
    def __init__(self, funcname: str, lineno: int, source: str) -> None:
        self._target_funcnames = (
            (funcname,)
            if funcname
            else (
                'print',
                'show',
                'format',
                'format_list',
                'debug',
                'info',
                'success',
                'warning',
                'error',
            )
        )
        self._target_lineno = lineno
        self._source_lines = source.splitlines()
        self.varnames: tp.List[tp.Optional[str]] = []
        self.found = False

    def _get_node_source(self, node: ast.AST) -> str:
        source = '\n'.join(self._source_lines)
        result = ast.get_source_segment(source, node)
        return result if result else ''

    def visit_Call(self, node: ast.Call) -> None:
        if node.lineno == self._target_lineno:
            funcname = ''
            if isinstance(node.func, ast.Name):
                funcname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    funcname = node.func.attr
            if funcname and funcname in self._target_funcnames:
                self.found = True
                for i, arg in enumerate(node.args):
                    # dprint(i, arg, type(arg))
                    if isinstance(arg, ast.Name):
                        self.varnames.append(arg.id)
                    elif isinstance(arg, ast.Call):
                        try:
                            source_text = self._get_node_source(arg)
                            self.varnames.append(source_text)
                        except (AttributeError, IndexError):
                            self.varnames.append(None)
                    else:
                        self.varnames.append(None)
        self.generic_visit(node)


def get_varnames(
    filepath: str, lineno: int, funcname: str = ''
) -> tp.Sequence[tp.Optional[str]]:
    """
    warning: do not call this function too frequently, it may cause performance
    issue. currently, only `./frame.py:FrameInfo:varnames` and
    `./format.py : format_list : if len(varnames) != len(args) ...` use this.
    """
    source, tree = _parse_ast(filepath)
    if tree:
        analyzer = VarnamesAnalyzer(funcname, lineno, source)
        analyzer.visit(tree)
        if analyzer.found:
            return analyzer.varnames
    return ()


_cache = {}  # {(filepath, time): (str, ast.AST | None), ...}


def _parse_ast(filepath: str) -> tp.Tuple[str, tp.Optional[ast.AST]]:
    time = os.stat(filepath).st_mtime
    if (key := (filepath, time)) in _cache:
        return _cache[key]
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            tree = None
        _cache[key] = (source, tree)
        return source, tree
