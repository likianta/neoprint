import neoprint as np
from pprint import pformat

np.debugger.enabled = True


def foo():
    np.show(':i', 'AAA - 1st')
    bar()
    np.show(':i', 'AAA - 4th')


def bar():
    np.show(':p1i', 'AAA - 2nd')
    baz()
    
    name = 'Alice'
    age = 20
    city = 'New York'
    np.show(name, age, city, ':np')


def baz():
    np.show(':p2i', 'AAA - 3rd')


foo()
outputs = tuple(map(np.util.strip_ansi, np.debugger.output))
assert outputs == (
    'change_parent_pointer.py:8   | [1] AAA - 1st\n',
    'change_parent_pointer.py:9   | [2] AAA - 2nd\n',
    'change_parent_pointer.py:9   | [3] AAA - 3rd\n',
    'change_parent_pointer.py:9   | name = "Alice"; age = 20; city = "New York"\n',
    'change_parent_pointer.py:10  | [4] AAA - 4th\n',
), pformat(outputs)
