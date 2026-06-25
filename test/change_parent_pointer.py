import neoprint as np
from contextlib import contextmanager
from pprint import pformat

np.debugger.enabled = True


def foo():
    np.show(':i', 'AAA - 1st')
    bar()
    np.show(':i', 'AAA - 5th')


def bar():
    np.show(':p1i', 'AAA - 2nd')
    with baz():
        name = 'Alice'
        age = 20
        city = 'New York'
        np.show(name, age, city, ':np')


@contextmanager
def baz():
    np.show(':p3i', 'AAA - 3rd')
    yield
    np.show(':p3i', 'AAA - 4th')


foo()
outputs = tuple(map(np.util.strip_ansi, np.debugger.output))
assert outputs == (
    'change_parent_pointer.py:9   | [1] AAA - 1st\n',
    'change_parent_pointer.py:10  | [2] AAA - 2nd\n',
    'change_parent_pointer.py:10  | [3] AAA - 3rd\n',
    'change_parent_pointer.py:10  | name = "Alice"; age = 20; city = "New York"\n',
    'change_parent_pointer.py:10  | [4] AAA - 4th\n',
    'change_parent_pointer.py:11  | [5] AAA - 5th\n',
), pformat(outputs)
