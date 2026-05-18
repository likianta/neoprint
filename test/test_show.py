import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import neoprint as np


def test_basic_show():
    print('=' * 60)
    print('Test 1: Basic show()')
    print('=' * 60)
    np.show('Hello, World!')
    np.show('Multiple', 'arguments', 'here')
    np.show(123, 456, 123 + 456)


def test_markup_parsing():
    print('\n' + '=' * 60)
    print('Test 2: Markup parsing')
    print('=' * 60)

    parser = np.MarkupParser()

    test_cases = [
        ':i',
        ':i1',
        ':i2',
        ':v',
        ':v0',
        ':v4',
        ':v8',
        ':c',
        ':c0',
        ':c2',
        ':p',
        ':p1',
        ':p2',
        ':d',
        ':d1',
    ]

    for markup in test_cases:
        marks = parser.parse(markup)
        print(f'{markup:8} -> color={marks.color}, index={marks.index}, '
              f'verbosity={marks.verbosity}, parent={marks.parent}, divider={marks.divider}')


def test_short_notation():
    print('\n' + '=' * 60)
    print('Test 3: Short notation at different positions')
    print('=' * 60)

    parser = np.MarkupParser()

    args1 = (':v4', 'first', 'second')
    args2 = ('first', 'second', ':v4')
    args3 = ('no markup',)

    for args in [args1, args2, args3]:
        raw_args, pos, marks = parser.extract_from_args(args)
        print(f'Input: {args}')
        print(f'  -> raw_args={raw_args}, pos={pos}, verbosity={marks.verbosity}')


def test_color_levels():
    print('\n' + '=' * 60)
    print('Test 4: Color levels')
    print('=' * 60)

    np.show('Default text (level 0)')
    np.show(':v1', 'Magenta (level 1) - negative info')
    np.show(':v2', 'Blue (level 2) - info')
    np.show(':v3', 'Dim green (level 3) - weak success')
    np.show(':v4', 'Bright green (level 4) - success')
    np.show(':v5', 'Dim yellow (level 5) - weak warning')
    np.show(':v6', 'Bright yellow (level 6) - warning')
    np.show(':v7', 'Dim red (level 7) - weak error')
    np.show(':v8', 'Bright red (level 8) - error')


def test_index():
    print('\n' + '=' * 60)
    print('Test 5: Index feature')
    print('=' * 60)

    np.show(':i', 'Item 1')
    np.show(':i', 'Item 2')
    np.show(':i', 'Item 3')

    print('Reset index:')
    np.show(':i0')

    np.show(':i', 'Item A')
    np.show(':i', 'Item B')


def test_parent_pointer():
    print('\n' + '=' * 60)
    print('Test 6: Parent pointer')
    print('=' * 60)

    def inner_function():
        np.show('From inner (default parent=p1)', ':p')

    def outer_function():
        np.show('From outer')
        inner_function()

    outer_function()


def test_divider():
    print('\n' + '=' * 60)
    print('Test 7: Divider')
    print('=' * 60)

    np.show(':d', 'Section start')
    np.show('Content line 1')
    np.show('Content line 2')
    np.show('Content line 3')


def test_show_varnames():
    print('\n' + '=' * 60)
    print('Test 8: Show varnames')
    print('=' * 60)

    name = 'Alice'
    age = 30
    city = 'New York'

    np.show(name, age, city, markup=':v')


def test_console_functions():
    print('\n' + '=' * 60)
    print('Test 9: Console utility functions')
    print('=' * 60)

    print(f'Console width: {np.get_console_width()}')
    print(f'Colored text: {np.color_text("Hello!", np.AnsiColor.GREEN)}')
    print(f'Stripped: {repr(np.strip_ansi(np.color_text("Hello!", np.AnsiColor.RED)))}')


if __name__ == '__main__':
    test_basic_show()
    test_markup_parsing()
    test_short_notation()
    test_color_levels()
    test_index()
    test_parent_pointer()
    test_divider()
    test_show_varnames()
    test_console_functions()

    print('\n' + '=' * 60)
    print('All tests completed!')
    print('=' * 60)
