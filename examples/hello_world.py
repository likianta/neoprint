import neoprint as np


def print_divider(text):
    np.show(':d')
    print(text)


def main():
    np.show(':i0')
    print_divider('Basic Usage')
    np.show('Hello, World!')
    np.show('Multiple', 'arguments', 'are', 'semicolon-separated')
    np.show(123, 456, 'mixed types', True, None)

    print_divider('Verbosity Levels (:v0-:v8)')
    np.show(':v0', 'DEBUG message (bright_black)')
    np.show(':v1', 'INFO (negative) - magenta')
    np.show(':v2', 'INFO (positive) - blue')
    np.show(':v3', 'WEAK SUCCESS - dim green')
    np.show(':v4', 'SUCCESS - bright green')
    np.show(':v5', 'WEAK WARNING - dim yellow')
    np.show(':v6', 'WARNING - bright yellow')
    np.show(':v7', 'WEAK ERROR - dim red')
    np.show(':v8', 'ERROR - bright red')

    print_divider('Index Counter Design')
    print_divider(':i (scope-level counter, default)')
    np.show(':i', 'module-level 1st')
    np.show(':i', 'module-level 2nd')
    np.show(':i', 'module-level 3rd')

    def inner_function():
        np.show(':i', 'function-level 1st')
        np.show(':i', 'function-level 2nd')
        np.show(':i', 'function-level 3rd')

    inner_function()
    np.show(':i', 'module-level 4th')

    print_divider(':i0 (reset all counters)')
    np.show(':i0')
    np.show(':i', 'start from 1 again')

    print_divider(':i1 (line-level counter)')
    for i in range(3):
        np.show(':i1', 'loop iteration', i)

    print_divider(':i3 (global-level counter)')
    np.show(':i3', 'global 1st')
    np.show(':i3', 'global 2nd')
    np.show(':i3', 'global 3rd')

    print_divider('Custom Scopes (np.scope)')
    with np.scope():
        np.show(':i', 'anonymous scope 1st')
        np.show(':i', 'anonymous scope 2nd')

    with np.scope(name='MyScope'):
        np.show(':i', 'MyScope 1st')
        np.show(':i', 'MyScope 2nd')
        np.show(':i', 'MyScope 3rd')

    print_divider('Variable Names (:v)')
    name = 'Alice'
    age = 30
    city = 'New York'
    np.show(name, age, city, markup=':v')

    print_divider('Combined Markups')
    np.show(':v4:i', 'success with scope index')
    np.show(':v6:i1', 'warning with line index')
    np.show(':v4:i3', 'success with global index')

    print_divider('Color Shorthand (:c)')
    np.show(':c2', 'cyan text')
    np.show(':c4', 'green text')
    np.show(':c6', 'yellow text')
    np.show(':c8', 'red text')


if __name__ == '__main__':
    main()
