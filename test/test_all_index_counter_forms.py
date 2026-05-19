import unittest
from unittest import TestCase

import neoprint as np


class TestIndexCounterForms(TestCase):
    def setUp(self):
        np.config(show_source=False, show_funcname=False)

    def test_i0_resets_all_counters(self):
        np.format(':i0')
        np.format(':i', 'first')
        np.format(':i', 'second')
        np.format(':i3', 'global')

        self.assertEqual(np.format(':i0'), '')
        result = np.format(':i', 'after reset')
        self.assertEqual(result, '[1] after reset')

    def test_i1_line_level_counter(self):
        for i in range(3):
            result = np.format(':i1', 'line', i)
            self.assertEqual(result, '[{}] line; {}'.format(i + 1, i))

    def test_i2_scope_level_counter(self):
        np.format(':i0')
        result1 = np.format(':i2', 'scope 1')
        result2 = np.format(':i2', 'scope 2')
        self.assertEqual(result1, '[1] scope 1')
        self.assertEqual(result2, '[2] scope 2')

    def test_i3_global_level_counter(self):
        np.format(':i0')

        def inner():
            return np.format(':i3', 'global')

        r1 = np.format(':i3', 'module 1')
        r2 = inner()
        r3 = np.format(':i3', 'module 2')

        self.assertEqual(r1, '[1] module 1')
        self.assertEqual(r2, '[2] global')
        self.assertEqual(r3, '[3] module 2')

    def test_i_shorthand_equals_i2(self):
        np.format(':i0')
        result_i = np.format(':i', 'shorthand')
        result_i2 = np.format(':i2', 'explicit')
        self.assertEqual(result_i, '[1] shorthand')
        self.assertEqual(result_i2, '[2] explicit')

    def test_scope_level_isolation(self):
        np.format(':i0')

        def func_a():
            return np.format(':i', 'func_a')

        def func_b():
            return np.format(':i', 'func_b')

        self.assertEqual(func_a(), '[1] func_a')
        self.assertEqual(func_a(), '[2] func_a')
        self.assertEqual(func_b(), '[1] func_b')

    def test_custom_scope_isolation(self):
        np.format(':i0')
        np.format(':i', 'before')

        with np.scope(name='Custom'):
            np.format(':i', 'custom 1')
            np.format(':i', 'custom 2')

        np.format(':i', 'after')

        self.assertEqual(np.format(':i', 'after scope'), '[3] after scope')

    def test_nested_scopes(self):
        np.format(':i0')

        with np.scope(name='Outer'):
            self.assertEqual(np.format(':i', 'outer 1'), '[1] outer 1')

            with np.scope(name='Inner'):
                self.assertEqual(np.format(':i', 'inner 1'), '[1] inner 1')
                self.assertEqual(np.format(':i', 'inner 2'), '[2] inner 2')

            self.assertEqual(np.format(':i', 'outer 2'), '[2] outer 2')

    def test_combined_markup_with_index(self):
        np.format(':i0')
        np.format(':v4:i', 'success with index')
        np.format(':v6:i1', 'warning with line index')
        np.format(':v4:i3', 'success with global index')
        np.format(':v2:i2', 'cyan with scope index')

    def test_line_counter_same_line(self):
        np.format(':i0')

        with np.capture_output(color_code_scheme='none') as output:
            np.show(':i1', 'call')

        lines = output.output[0].strip().split('\n')
        self.assertEqual(len(lines), 1)
        self.assertIn('[1]', lines[0])

        for i in range(3):
            result = np.format(':i1', 'line', i)
            self.assertEqual(result, '[{}] line; {}'.format(i + 1, i))

    def test_reset_does_not_affect_global_counter(self):
        np.format(':i0')
        np.format(':i', 'scope')
        np.format(':i3', 'global')

        np.format(':i0')

        self.assertEqual(
            np.format(':i', 'scope after reset'), '[1] scope after reset'
        )
        self.assertEqual(
            np.format(':i3', 'global after reset'), '[1] global after reset'
        )

    def test_anonymous_scope_generates_unique_id(self):
        np.format(':i0')

        with np.scope():
            result1 = np.format(':i', 'anonymous 1')
            self.assertEqual(result1, '[1] anonymous 1')

        with np.scope():
            result2 = np.format(':i', 'anonymous 2')
            self.assertEqual(result2, '[1] anonymous 2')

    def test_scope_stack_nesting(self):
        np.format(':i0')

        with np.scope(name='A'):
            self.assertEqual(np.format(':i', 'A1'), '[1] A1')

            with np.scope(name='B'):
                self.assertEqual(np.format(':i', 'B1'), '[1] B1')

                with np.scope(name='C'):
                    self.assertEqual(np.format(':i', 'C1'), '[1] C1')
                    self.assertEqual(np.format(':i', 'C2'), '[2] C2')

                self.assertEqual(np.format(':i', 'B2'), '[2] B2')

            self.assertEqual(np.format(':i', 'A2'), '[2] A2')

    def test_all_four_index_levels_independently(self):
        np.format(':i0')

        np.format(':i1', 'line')
        np.format(':i2', 'scope')
        np.format(':i3', 'global')

        np.format(':i1', 'line')
        np.format(':i2', 'scope')
        np.format(':i3', 'global')

        self.assertEqual(np.format(':i1', 'line'), '[1] line')
        self.assertEqual(np.format(':i2', 'scope'), '[3] scope')
        self.assertEqual(np.format(':i3', 'global'), '[3] global')

    def test_scope_resumes_after_inner_scope_ends(self):
        np.format(':i0')

        with np.scope(name='Outer'):
            self.assertEqual(np.format(':i', 'outer 1'), '[1] outer 1')

            with np.scope(name='Inner'):
                self.assertEqual(np.format(':i', 'inner 1'), '[1] inner 1')

            self.assertEqual(np.format(':i', 'outer 2'), '[2] outer 2')

    def test_global_counter_accumulates_across_scopes(self):
        np.format(':i0')

        with np.scope(name='A'):
            self.assertEqual(np.format(':i3', 'A1'), '[1] A1')

            with np.scope(name='B'):
                self.assertEqual(np.format(':i3', 'B1'), '[2] B1')

        self.assertEqual(np.format(':i3', 'module'), '[3] module')


if __name__ == '__main__':
    unittest.main()
