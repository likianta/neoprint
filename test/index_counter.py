import neoprint as np

np.config(show_funcname=True)


def main():
    for i in range(10):
        if i % 2 == 0:
            np.show('number is even', i, ':i2')
        else:
            np.show('number is odd', i, ':i2')

    np.show(':d', 'separately count')
    for i in range(10):
        if i % 2 == 0:
            np.show('number is even', i, ':i1')
        else:
            np.show('number is odd', i, ':i1')


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
main()
