import neoprint as np

np.config(show_source=False, show_funcname=False)
np.debug.enabled = True

np.show(':i', 'AAA - 1st')
assert np.util.strip_ansi(np.debug.output[-1]) == '[1] AAA - 1st\n'
np.show(':i', 'AAA - 2nd')
assert np.util.strip_ansi(np.debug.output[-1]) == '[2] AAA - 2nd\n'
np.show(':i', 'AAA - 3rd')
assert np.util.strip_ansi(np.debug.output[-1]) == '[3] AAA - 3rd\n'


def main() -> None:
    np.show(':i', 'BBB - 1st')
    assert np.util.strip_ansi(np.debug.output[-1]) == '[1] BBB - 1st\n'
    np.show(':i', 'BBB - 2nd')
    assert np.util.strip_ansi(np.debug.output[-1]) == '[2] BBB - 2nd\n'
    np.show(':i', 'BBB - 3rd')
    assert np.util.strip_ansi(np.debug.output[-1]) == '[3] BBB - 3rd\n'

    def inner_function(time_called: int):
        if time_called == 1:
            np.show(':i', 'CCC - 1st')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[1] CCC - 1st\n'
            np.show(':i', 'CCC - 2nd')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[2] CCC - 2nd\n'
            np.show(':i', 'CCC - 3rd')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[3] CCC - 3rd\n'
        elif time_called == 2:
            np.show(':i', 'CCC - 4th')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[4] CCC - 4th\n'
            np.show(':i', 'CCC - 5th')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[5] CCC - 5th\n'
            np.show(':i', 'CCC - 6th')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[6] CCC - 6th\n'

    inner_function(1)
    inner_function(2)

    np.show(':i', 'BBB - 4th')
    assert np.util.strip_ansi(np.debug.output[-1]) == '[4] BBB - 4th\n'
    np.show(':i', 'BBB - 5th')
    assert np.util.strip_ansi(np.debug.output[-1]) == '[5] BBB - 5th\n'
    np.show(':i', 'BBB - 6th')
    assert np.util.strip_ansi(np.debug.output[-1]) == '[6] BBB - 6th\n'

    with np.scope():
        np.show(':i', 'custom scope - 1st')
        assert np.util.strip_ansi(np.debug.output[-1]) == '[1] custom scope - 1st\n'
        np.show(':i', 'custom scope - 2nd')
        assert np.util.strip_ansi(np.debug.output[-1]) == '[2] custom scope - 2nd\n'
        np.show(':i', 'custom scope - 3rd')
        assert np.util.strip_ansi(np.debug.output[-1]) == '[3] custom scope - 3rd\n'

        with np.scope(name='DDD'):
            np.show(':i', 'DDD - 1st')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[1] DDD - 1st\n'
            np.show(':i', 'DDD - 2nd')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[2] DDD - 2nd\n'
            np.show(':i', 'DDD - 3rd')
            assert np.util.strip_ansi(np.debug.output[-1]) == '[3] DDD - 3rd\n'

    for i in range(3):
        np.show(':i1', 'line-level', 'EEE')
        assert np.util.strip_ansi(np.debug.output[-1]) == '[{}] line-level; EEE\n'.format(i + 1)


if __name__ == '__main__':
    main()