import ast
import typing as tp
from functools import cache


class VarnamesAnalyzer(ast.NodeVisitor):
    def __init__(self, funcname: str, lineno: int) -> None:
        self._target_funcnames = (
            (funcname,)
            if funcname
            else (
                'format',
                'format_list',
                'show',
                'print',
                'debug',
                'info',
                'success',
                'warning',
                'error',
            )
        )
        self._target_lineno = lineno
        self.varnames: tp.List[tp.Optional[str]] = []
        self.found = False

    def visit_Call(self, node: ast.Call) -> None:
        if node.lineno == self._target_lineno:
            # dprint(node.func)
            funcname = ''
            if isinstance(node.func, ast.Name):
                funcname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    funcname = node.func.attr
            if funcname and funcname in self._target_funcnames:
                self.found = True
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        self.varnames.append(arg.id)
                    else:
                        self.varnames.append(None)
        self.generic_visit(node)


def get_varnames(
    filepath: str, lineno: int, funcname: str = ''
) -> tp.Sequence[tp.Optional[str]]:
    if tree := _parse_ast(filepath):
        analyzer = VarnamesAnalyzer(funcname, lineno)
        analyzer.visit(tree)
        if analyzer.found:
            return analyzer.varnames
    return ()


@cache
def _parse_ast(filepath: str) -> tp.Optional[ast.AST]:
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        return ast.parse(source)
    except SyntaxError:
        return None
