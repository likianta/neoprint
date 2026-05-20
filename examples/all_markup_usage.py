import neoprint as np


def main():
    np.show(':i0')
    np.show(':d', 'Basic Usage')
    np.show('Hello, World!')
    np.show('Multiple', 'arguments', 'are', 'semicolon-separated')
    np.show(123, 456, 'mixed types', True, None)

    np.show(':d', 'Verbosity Levels (:v0-:v8)')
    np.show(':v1', 'DEBUG message (bright_black)')
    np.show(':v2', 'INFO - cyan')
    np.show(':v3', 'WEAK SUCCESS - dim green')
    np.show(':v4', 'SUCCESS - bright green')
    np.show(':v5', 'WEAK WARNING - dim yellow')
    np.show(':v6', 'WARNING - bright yellow')
    np.show(':v7', 'WEAK ERROR - dim red')
    np.show(':v8', 'ERROR - bright red')

    np.show(':d', 'Index Counter Design')
    np.show(':i', 'module-level 1st')
    np.show(':i', 'module-level 2nd')
    np.show(':i', 'module-level 3rd')

    def inner_function():
        np.show(':i', 'function-level 1st')
        np.show(':i', 'function-level 2nd')
        np.show(':i', 'function-level 3rd')

    inner_function()
    np.show(':i', 'module-level 4th')

    np.show(':d', ':i0 (reset all counters)')
    np.show(':i0')
    np.show(':i', 'start from 1 again')

    np.show(':d', ':i1 (line-level counter)')
    for i in range(3):
        np.show(':i1', 'loop iteration', i)

    np.show(':d', ':i3 (global-level counter)')
    np.show(':i3', 'global 1st')
    np.show(':i3', 'global 2nd')
    np.show(':i3', 'global 3rd')

    np.show(':d', 'Custom Scopes (np.scope)')
    with np.scope():
        np.show(':i', 'anonymous scope 1st')
        np.show(':i', 'anonymous scope 2nd')

    with np.scope(name='MyScope'):
        np.show(':i', 'MyScope 1st')
        np.show(':i', 'MyScope 2nd')
        np.show(':i', 'MyScope 3rd')

    np.show(':d', 'Variable Names (:n)')
    name = 'Alice'
    age = 30
    city = 'New York'
    np.show(name, age, city, markup=':n')

    np.show(':d', 'Combined Markups')
    np.show(':v4i', 'success with scope index')
    np.show(':v6i1', 'warning with line index')
    np.show(':v4i3', 'success with global index')


if __name__ == '__main__':
    main()
