import ast
import os
import typing as tp
from collections import namedtuple


class T:
    CachedData = namedtuple('CachedData', ('file', 'time', 'source', 'tree'))
    CachedFiles = tp.Dict[str, CachedData]


_cache: T.CachedFiles = {}


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
        self._source = source
        self.varnames: tp.List[tp.Optional[str]] = []
        self.found = False

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
                        if x := self._reveal_source_of_call(arg):
                            self.varnames.append(x)
                        else:
                            self.varnames.append(None)
                    else:
                        self.varnames.append(None)
        self.generic_visit(node)

    def _reveal_source_of_call(self, node: ast.Call) -> str:
        return ast.get_source_segment(self._source, node) or ''


def get_varnames(
    filepath: str, lineno: int, funcname: str = ''
) -> tp.Sequence[tp.Optional[str]]:
    """
    warning: do not call this function too frequently, it may cause performance
    issue. currently, only `./frame.py:FrameInfo:varnames` and
    `./format.py : format_list : if len(varnames) != len(args) ...` use this.
    """
    data = _parse_ast(filepath)
    if data.tree:
        analyzer = VarnamesAnalyzer(funcname, lineno, data.source)
        analyzer.visit(data.tree)
        if analyzer.found:
            return analyzer.varnames
    return ()


def _parse_ast(filepath: str) -> T.CachedData:
    mtime = os.stat(filepath).st_mtime
    if filepath not in _cache or _cache[filepath].time != mtime:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            tree = None
        _cache[filepath] = T.CachedData(
            file=filepath, time=mtime, source=source, tree=tree
        )
    return _cache[filepath]
