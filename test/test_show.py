import pytest
import neoprint as np
from neoprint.markup import MarkupParser, ParsedMarks


class TestMarkupParser:
    def setup_method(self):
        self.parser = MarkupParser()

    def test_is_valid_markup_single(self):
        assert self.parser.is_valid_markup(':i')
        assert self.parser.is_valid_markup(':v')
        assert self.parser.is_valid_markup(':p')
        assert self.parser.is_valid_markup(':n')
        assert self.parser.is_valid_markup(':d')
        assert self.parser.is_valid_markup(':r')
        assert self.parser.is_valid_markup(':t')
        assert self.parser.is_valid_markup(':f')
        assert self.parser.is_valid_markup(':l')
        assert self.parser.is_valid_markup(':s')

    def test_is_valid_markup_with_number(self):
        assert self.parser.is_valid_markup(':i0')
        assert self.parser.is_valid_markup(':i1')
        assert self.parser.is_valid_markup(':v4')
        assert self.parser.is_valid_markup(':v8')
        assert self.parser.is_valid_markup(':p1')
        assert self.parser.is_valid_markup(':p2')
        assert self.parser.is_valid_markup(':n1')

    def test_is_valid_markup_combined(self):
        assert self.parser.is_valid_markup(':v4i')
        assert self.parser.is_valid_markup(':nv')

    def test_is_valid_markup_invalid(self):
        assert not self.parser.is_valid_markup('i')
        assert not self.parser.is_valid_markup(':invalid')
        assert not self.parser.is_valid_markup(':9')

    def test_parse_index(self):
        marks = self.parser.parse(':i')
        assert marks.index == 2

        marks = self.parser.parse(':i0')
        assert marks.index == 0

        marks = self.parser.parse(':i1')
        assert marks.index == 1

        marks = self.parser.parse(':i2')
        assert marks.index == 2

        marks = self.parser.parse(':i3')
        assert marks.index == 3

    def test_parse_parent(self):
        marks = self.parser.parse(':p')
        assert marks.parent == 1

        marks = self.parser.parse(':p0')
        assert marks.parent == 0

        marks = self.parser.parse(':p1')
        assert marks.parent == 1

        marks = self.parser.parse(':p2')
        assert marks.parent == 2

    def test_parse_verbosity(self):
        marks = self.parser.parse(':v')
        assert marks.verbosity == 0

        marks = self.parser.parse(':v0')
        assert marks.verbosity == 0

        marks = self.parser.parse(':v4')
        assert marks.verbosity == 4

        marks = self.parser.parse(':v8')
        assert marks.verbosity == 8

    def test_parse_show_varnames(self):
        marks = self.parser.parse(':n')
        assert marks.show_varnames == 1

        marks = self.parser.parse(':n0')
        assert marks.show_varnames == 0

        marks = self.parser.parse(':n1')
        assert marks.show_varnames == 1

    def test_parse_divider(self):
        marks = self.parser.parse(':d')
        assert marks.divider == 0

        marks = self.parser.parse(':d1')
        assert marks.divider == 1

    def test_parse_rich(self):
        marks = self.parser.parse(':r')
        assert marks.rich == 0

        marks = self.parser.parse(':r1')
        assert marks.rich == 1

    def test_parse_timer(self):
        marks = self.parser.parse(':t')
        assert marks.timer == 1

        marks = self.parser.parse(':t0')
        assert marks.timer == 0

        marks = self.parser.parse(':t2')
        assert marks.timer == 2

    def test_parse_expand(self):
        marks = self.parser.parse(':l')
        assert marks.expand == 0

        marks = self.parser.parse(':l1')
        assert marks.expand == 1

    def test_parse_short(self):
        marks = self.parser.parse(':s')
        assert marks.short == 0

        marks = self.parser.parse(':s1')
        assert marks.short == 1

    def test_parse_flush(self):
        marks = self.parser.parse(':f')
        assert marks.flush == 0

        marks = self.parser.parse(':f1')
        assert marks.flush == 1

    def test_parse_combined(self):
        marks = self.parser.parse(':v4i')
        assert marks.verbosity == 4
        assert marks.index == 2

    def test_extract_from_args_no_markup(self):
        args = ('hello', 'world')
        raw_args, pos, marks = self.parser.extract_from_args(args)
        assert raw_args == args
        assert pos == 0
        assert marks.index is None
        assert marks.verbosity is None

    def test_extract_from_args_markup_first(self):
        args = (':v4', 'hello', 'world')
        raw_args, pos, marks = self.parser.extract_from_args(args)
        assert raw_args == ('hello', 'world')
        assert pos == 1
        assert marks.verbosity == 4

    def test_extract_from_args_markup_last(self):
        args = ('hello', 'world', ':v4')
        raw_args, pos, marks = self.parser.extract_from_args(args)
        assert raw_args == ('hello', 'world')
        assert pos == -1
        assert marks.verbosity == 4


class TestFrameInfo:
    def test_caller_frame_has_info(self):
        frame = np.FrameInfo('test.py', 10, 'test_func')
        assert frame.filepath == 'test.py'
        assert frame.lineno == 10
        assert frame.funcname == 'test_func'

    def test_frame_id(self):
        frame = np.FrameInfo('test.py', 10, 'test_func')
        assert frame.id == 'test.py:10'

    def test_filename(self):
        frame = np.FrameInfo('/path/to/test.py', 10, 'test_func')
        assert frame.filename == 'test.py'


class TestConsoleFunctions:
    def test_get_console_width(self):
        width = np.get_console_width()
        assert isinstance(width, int)
        assert width > 0

    def test_color_text(self):
        colored = np.color_text('hello', np.AnsiColor.RED)
        assert '\033[' in colored
        assert 'hello' in colored
        assert '\033[0m' in colored

    def test_strip_ansi(self):
        colored = np.color_text('hello', np.AnsiColor.RED)
        stripped = np.strip_ansi(colored)
        assert stripped == 'hello'
        assert '\033[' not in stripped


class TestShowFunction:
    def test_show_basic(self, capsys):
        np.show('hello', 'world')
        captured = capsys.readouterr()
        assert 'hello' in captured.out
        assert 'world' in captured.out

    def test_show_single_arg(self, capsys):
        np.show('hello')
        captured = capsys.readouterr()
        assert 'hello' in captured.out

    def test_show_multiple_args_space_separated(self, capsys):
        np.show('a', 'b', 'c')
        captured = capsys.readouterr()
        stripped = np.strip_ansi(captured.out)
        assert '"a"; "b"; "c"' in stripped

    def test_show_with_markup_first(self, capsys):
        np.show(':v4', 'success message')
        captured = capsys.readouterr()
        assert 'success message' in captured.out
        assert '\033[' in captured.out

    def test_show_with_markup_last(self, capsys):
        np.show('info message', ':v2')
        captured = capsys.readouterr()
        assert 'info message' in captured.out

    def test_show_with_verbosity_level(self, capsys):
        np.show(':v8', 'error message')
        captured = capsys.readouterr()
        assert 'error message' in captured.out

    def test_show_with_index(self, capsys):
        np.show(':i', 'item 1')
        np.show(':i', 'item 2')
        captured = capsys.readouterr()
        assert 'item 1' in captured.out
        assert 'item 2' in captured.out

    def test_show_reset_index(self, capsys):
        np.show(':i', 'item 1')
        np.show(':i0')
        captured = capsys.readouterr()
        assert 'item 1' in captured.out

    def test_show_divider(self, capsys):
        np.show(':d', 'section')
        captured = capsys.readouterr()
        assert 'section' in captured.out

    def test_show_integer_args(self, capsys):
        np.show(1, 2, 3)
        captured = capsys.readouterr()
        assert '1' in captured.out
        assert '2' in captured.out
        assert '3' in captured.out

    def test_show_mixed_args(self, capsys):
        np.show('string', 123, True, None)
        captured = capsys.readouterr()
        assert 'string' in captured.out
        assert '123' in captured.out
        assert 'True' in captured.out
        assert 'None' in captured.out


class TestShowVarnames:
    def test_show_varnames_disabled_by_default(self, capsys):
        name = 'Alice'
        age = 30
        np.show(name, age)
        captured = capsys.readouterr()
        assert 'Alice' in captured.out
        assert '30' in captured.out
        assert 'name =' not in captured.out

    def test_show_varnames_enabled(self, capsys):
        np.config.show_varnames = True
        name = 'Alice'
        age = 30
        np.show(name, age)
        np.config.show_varnames = False
        captured = capsys.readouterr()
        assert 'Alice' in captured.out
        assert '30' in captured.out


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
