import neoprint as np

np.config(show_source=False, show_funcname=False)

assert np.format(':i', 'AAA - 1st') == '[1] AAA - 1st'
assert np.format(':i', 'AAA - 2nd') == '[2] AAA - 2nd'
assert np.format(':i', 'AAA - 3rd') == '[3] AAA - 3rd'


def main() -> None:
    assert np.format(':i', 'BBB - 1st') == '[1] BBB - 1st'
    assert np.format(':i', 'BBB - 2nd') == '[2] BBB - 2nd'
    assert np.format(':i', 'BBB - 3rd') == '[3] BBB - 3rd'

    def inner_function(time_called: int):
        if time_called == 1:
            assert np.format(':i', 'CCC - 1st') == '[1] CCC - 1st'
            assert np.format(':i', 'CCC - 2nd') == '[2] CCC - 2nd'
            assert np.format(':i', 'CCC - 3rd') == '[3] CCC - 3rd'
        elif time_called == 2:
            assert np.format(':i', 'CCC - 4th') == '[4] CCC - 4th'
            assert np.format(':i', 'CCC - 5th') == '[5] CCC - 5th'
            assert np.format(':i', 'CCC - 6th') == '[6] CCC - 6th'

    inner_function(1)
    inner_function(2)

    assert np.format(':i', 'BBB - 4th') == '[4] BBB - 4th'
    assert np.format(':i', 'BBB - 5th') == '[5] BBB - 5th'
    assert np.format(':i', 'BBB - 6th') == '[6] BBB - 6th'

    with np.scope():  # will create a new scope with a random name.
        assert np.format(':i', 'custom scope - 1st') == '[1] custom scope - 1st'
        assert np.format(':i', 'custom scope - 2nd') == '[2] custom scope - 2nd'
        assert np.format(':i', 'custom scope - 3rd') == '[3] custom scope - 3rd'

        with np.scope(name='DDD'):
            assert np.format(':i', 'DDD - 1st') == '[1] DDD - 1st'
            assert np.format(':i', 'DDD - 2nd') == '[2] DDD - 2nd'
            assert np.format(':i', 'DDD - 3rd') == '[3] DDD - 3rd'

    for i in range(3):
        assert np.format(
            ':i1', 'line-level', 'EEE'
        ) == '[{}] line-level; EEE'.format(i + 1)


if __name__ == '__main__':
    main()
