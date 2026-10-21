import neoprint as np

np.config(show_funcname=True)
np.show('hello')


def foo():
    np.show('world')


foo()
