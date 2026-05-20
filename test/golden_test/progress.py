import neoprint as np
from faker import Faker
from time import sleep

fk = Faker()
np.config(debug_output=True)


def main():
    basic_usage()
    combined_markups()


def basic_usage():
    np.show(':d')
    np.show('Basic Usage')

    words = tuple(fk.sentence() for _ in range(20))
    with np.Progress(len(words)) as prog:
        for w in words:
            prog.update(w)
            # sleep(0.02)

    _validate_bbcode_output(1, _expected_bbcode_output(16, 'Basic Usage'))
    _validate_bbcode_output(
        2,
        _expected_bbcode_output(
            21,
            '[red]█[/]'
            '[bright_black]▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁[/] '
            '[red]\\[ 1/20][/] '
            '{}'.format(words[0]),
        ),
    )
    _validate_bbcode_output(
        -1,
        _expected_bbcode_output(
            21,
            '[red]████████████████████[/] [red]\\[20/20][/] {}'.format(
                words[-1]
            ),
        ),
    )
    np.debugger.output.clear()


def combined_markups():
    np.show(':d')
    np.show('Combined Markups')
    words = tuple(fk.sentence() for _ in range(20))
    with np.Progress(len(words)) as prog:
        for w in words:
            prog.update(*w.split(), markup=':v4p')
            # sleep(0.02)

    _validate_bbcode_output(1, _expected_bbcode_output(49, 'Combined Markups'))
    _validate_bbcode_output(
        2,
        _expected_bbcode_output(
            11,
            '[red]█[/]'
            '[bright_black]▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁[/] '
            '[red]\\[ 1/20][/] '
            '{}'.format(
                '[bright_black];[/] '.join(
                    ['[green]{}[/]'.format(x) for x in words[0].split()]
                )
            ),
        ),
    )
    np.debugger.output.clear()


def _expected_bbcode_output(lineno, *body_parts):
    return (
        '[bold blue]progress.py[/]'
        + '[dim blue]:[/]'
        + '[dim blue]{:<3}[/]'.format(lineno)
        + ' [bright_black]|[/] '
        + '[bright_black];[/] '.join(body_parts)
        + '\n'
    )


def _validate_bbcode_output(dbg_index: int, expected: str):
    actual = np.util.ansi_to_bbcode(np.debugger.output[dbg_index])
    assert actual == expected, np.format(expected, actual, ':nlv8')


if __name__ == '__main__':
    main()
