import ast
import os
from functools import lru_cache
from typing import List, Optional, Tuple


@lru_cache(maxsize=512)
def _read_source_lines(filepath: str) -> List[str]:
    if not os.path.isfile(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    except (OSError, UnicodeDecodeError):
        return []


def get_source_lines(filepath: str, lineno: int) -> List[str]:
    lines = _read_source_lines(filepath)
    if not lines:
        return []
    start = max(0, lineno - 1)
    end = min(len(lines), lineno)
    return lines[start:end]


@lru_cache(maxsize=512)
def get_source_code(filepath: str) -> str:
    lines = _read_source_lines(filepath)
    return ''.join(lines)


@lru_cache(maxsize=512)
def _parse_ast(filepath: str) -> Optional[ast.AST]:
    source = get_source_code(filepath)
    if not source:
        return None
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


class AstAnalyzer(ast.NodeVisitor):
    def __init__(self, target_lineno: int) -> None:
        self.target_lineno = target_lineno
        self.varnames: List[str] = []
        self.target_node: Optional[ast.AST] = None

    def visit_Expr(self, node: ast.Expr) -> None:
        if hasattr(node, 'lineno') and node.lineno == self.target_lineno:
            self.target_node = node
            self.generic_visit(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if hasattr(node, 'lineno') and node.lineno == self.target_lineno:
            self.target_node = node
            self.generic_visit(node)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if hasattr(node, 'lineno') and node.lineno == self.target_lineno:
            self.target_node = node
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.varnames.append(target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if hasattr(node, 'lineno') and node.lineno == self.target_lineno:
            self.target_node = node
            if isinstance(node.target, ast.Name):
                self.varnames.append(node.target.id)
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        if hasattr(node, 'lineno') and node.lineno == self.target_lineno:
            self.target_node = node
            if isinstance(node.target, ast.Name):
                self.varnames.append(node.target.id)
        self.generic_visit(node)


def get_varnames(filepath: str, lineno: int) -> Tuple[str, ...]:
    if not os.path.isfile(filepath):
        return ()
    tree = _parse_ast(filepath)
    if tree is None:
        return ()
    analyzer = AstAnalyzer(lineno)
    analyzer.visit(tree)
    return tuple(analyzer.varnames)


class CallSiteAnalyzer(ast.NodeVisitor):
    def __init__(self, funcname: str, target_lineno: int) -> None:
        self.funcname = funcname
        self.target_lineno = target_lineno
        self.args: List[str] = []
        self.found = False

    def visit_Call(self, node: ast.Call) -> None:
        if hasattr(node, 'lineno') and node.lineno == self.target_lineno:
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == self.funcname
            ):
                self.found = True
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        self.args.append(arg.id)
                    elif isinstance(arg, ast.Starred):
                        if isinstance(arg.value, ast.Name):
                            self.args.append('*' + arg.value.id)
        self.generic_visit(node)


def get_call_args(
    filepath: str, lineno: int, funcname: str = 'show'
) -> List[str]:
    if not os.path.isfile(filepath):
        return []
    tree = _parse_ast(filepath)
    if tree is None:
        return []
    analyzer = CallSiteAnalyzer(funcname, lineno)
    analyzer.visit(tree)
    return analyzer.args if analyzer.found else []


class VarnamesAnalyzer(ast.NodeVisitor):
    def __init__(
        self, funcname: str, target_lineno: int
    ) -> None:
        self.funcname = funcname
        self.target_lineno = target_lineno
        self.varnames: List[str] = []
        self.found = False

    def visit_Call(self, node: ast.Call) -> None:
        if hasattr(node, 'lineno') and node.lineno == self.target_lineno:
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    func_name = node.func.value.id + '.' + node.func.attr
            if func_name == self.funcname:
                self.found = True
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        self.varnames.append(arg.id)
                    elif isinstance(arg, ast.Constant):
                        self.varnames.append(repr(arg.value))
                    else:
                        self.varnames.append(None)
        self.generic_visit(node)


def get_varnames_from_call(
    filepath: str, lineno: int, funcname: str = 'show'
) -> Tuple[str, ...]:
    if not os.path.isfile(filepath):
        return ()
    tree = _parse_ast(filepath)
    if tree is None:
        return ()
    analyzer = VarnamesAnalyzer(funcname, lineno)
    analyzer.visit(tree)
    return tuple(analyzer.varnames) if analyzer.found else ()
