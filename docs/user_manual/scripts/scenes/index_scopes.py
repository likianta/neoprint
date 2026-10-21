import neoprint as np

np.config(show_funcname=True)

def foo():
    np.show(':i2', 'file A')
    np.show(':i2', 'file B')
    np.show(':i2', 'file C')
    np.show(':i2', 'file D')
    np.show(':i2', 'file E')

def bar():
    np.show(':i2', 'anonymous 1')
    np.show(':i2', 'anonymous 2')

foo()
bar()