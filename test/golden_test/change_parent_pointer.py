import neoprint as np

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
assert tuple(map(np.util.strip_ansi, np.debugger.output)) == (
    'change_parent_pointer.py:7   | [1] AAA - 1st\n',
    'change_parent_pointer.py:8   | [2] AAA - 2nd\n',
    'change_parent_pointer.py:8   | [3] AAA - 3rd\n',
    'change_parent_pointer.py:8   | name = "Alice"; age = 20; city = "New York"\n',
    'change_parent_pointer.py:9   | [4] AAA - 4th\n',
)
