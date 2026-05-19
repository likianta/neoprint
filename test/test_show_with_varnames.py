import pytest


class TestGetBodyString:
    def test_get_body_string_with_varnames(self):
        import neoprint as np

        name = 'Alice'
        age = 30
        city = 'New York'

        result = np.get_body_string(name, age, city, markup=':v')
        stripped = np.strip_ansi(result)
        assert 'name = "Alice"' in stripped
        assert 'age = 30' in stripped
        assert 'city = "New York"' in stripped

    def test_get_body_string_integration(self):
        import neoprint as np

        name = 'Alice'
        age = 30
        city = 'New York'

        result = np.get_body_string(name, age, city, markup=':v')
        stripped = np.strip_ansi(result)
        assert stripped == 'name = "Alice"; age = 30; city = "New York"'

    def test_get_body_string_without_varnames(self):
        import neoprint as np

        result = np.get_body_string('hello', 'world', markup='')
        stripped = np.strip_ansi(result)
        assert stripped == '"hello"; "world"'

    def test_get_body_string_with_color(self):
        import neoprint as np

        result = np.get_body_string('test', markup=':c4')
        assert '\033[' in result

    def test_get_body_string_mixed_types(self):
        import neoprint as np

        name = 'Bob'
        count = 42
        active = True

        result = np.get_body_string(name, count, active, markup=':v')
        stripped = np.strip_ansi(result)
        assert 'name = "Bob"' in stripped
        assert 'count = 42' in stripped
        assert 'active = True' in stripped

    def test_get_body_string_no_markup(self):
        import neoprint as np

        name = 'Alice'
        age = 30

        result = np.get_body_string(name, age)
        stripped = np.strip_ansi(result)
        assert stripped == '"Alice"; 30'

    def test_get_body_string_varnames_with_keyword(self):
        import neoprint as np

        name = 'Alice'
        city = 'New York'

        result = np.get_body_string(name, city, markup=':v')
        stripped = np.strip_ansi(result)
        assert 'name = "Alice"' in stripped
        assert 'city = "New York"' in stripped


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
