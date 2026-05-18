import neoprint as np


def print_divider(text):
    np.show(':d')
    np.show(text)


def main():
    print_divider('Basic Usage')
    np.show('Hello, World!')
    np.show('Multiple', 'arguments', 'are', 'space-separated')
    np.show(123, 456, 'mixed types', True, None)

    print_divider('Verbosity Levels (:v0-:v8)')
    np.show(':v0', 'DEBUG message (gray)')
    np.show(':v1', 'INFO (negative) - magenta')
    np.show(':v2', 'INFO (positive) - blue')
    np.show(':v3', 'WEAK SUCCESS - dim green')
    np.show(':v4', 'SUCCESS - bright green')
    np.show(':v5', 'WEAK WARNING - dim yellow')
    np.show(':v6', 'WARNING - bright yellow')
    np.show(':v7', 'WEAK ERROR - dim red')
    np.show(':v8', 'ERROR - bright red')

    print_divider('Indexing (:i)')
    np.show(':i', 'first item')
    np.show(':i', 'second item')
    np.show(':i', 'third item')
    np.show(':i0')
    np.show(':i', 'reset and start again')
    np.show(':i', 'another item')

    print_divider('Parent Frame Pointer (:p)')

    def inner():
        np.show('from inner function')
        np.show(':p', 'from parent (function level)')

    np.show('from main')
    inner()

    print_divider('Variable Names (varnames=1)')
    name = 'Alice'
    age = 30
    city = 'New York'
    np.show(name, age, city, markup=':v')

    print_divider('Combined Markups')
    np.show(':v4i', 'success with index')
    np.show(':v6i', 'warning with index')

    print_divider('Color Shorthand (:c)')
    np.show(':c2', 'cyan text')
    np.show(':c4', 'green text')
    np.show(':c6', 'yellow text')
    np.show(':c8', 'red text')


if __name__ == '__main__':
    main()
