import neoprint as np
from faker import Faker
from time import sleep
from testsuit import compose_bbcode_output
from testsuit import validate_bbcode_output

fk = Faker()
np.config(debug_output=True)


def main():
    basic_usage()
    combined_markups()
    no_residual_characters()


def basic_usage():
    np.show(':d', 'Basic Usage')

    words = tuple(fk.sentence() for _ in range(20))
    with np.Progress(len(words)) as prog:
        for w in words:
            prog.update(w)
            # sleep(0.02)

    output0 = np.util.ansi_to_bbcode(np.debugger.output[0])
    assert '─' in output0
    assert output0.replace('─', '') == compose_bbcode_output(
        18, ' Basic Usage '
    )

    validate_bbcode_output(
        1,
        compose_bbcode_output(
            23,
            '[red]██[/]'
            '[bright_black]▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁[/] '
            '[red]\\[ 1/20][/] '
            '{}'.format(words[0]),
        ),
    )
    validate_bbcode_output(
        -1,
        compose_bbcode_output(
            23,
            '[red]████████████████████████████████████████[/] [red]\\[20/20][/] {}'.format(
                words[-1]
            ),
        ),
    )


def combined_markups():
    np.debugger.output.clear()
    np.show(':d', 'Combined Markups')
    words = tuple(fk.sentence() for _ in range(20))
    with np.Progress(len(words)) as prog:
        for w in words:
            prog.update(*w.split(), markup=':v4p')
            # sleep(0.02)

    output0 = np.util.ansi_to_bbcode(np.debugger.output[0])
    assert '─── Combined Markups ───' in output0
    div_char_count = output0.count('─')
    assert div_char_count % 2 == 0
    validate_bbcode_output(
        0,
        compose_bbcode_output(
            55,
            '{} Combined Markups {}'.format(
                '─' * int(div_char_count / 2),
                '─' * int(div_char_count / 2),
            ),
        ),
    )
    validate_bbcode_output(
        1,
        compose_bbcode_output(
            13,
            '[red]██[/]'
            '[bright_black]▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁[/] '
            '[red]\\[ 1/20][/] '
            '{}'.format(
                '[bright_black];[/] '.join(
                    ['[green]{}[/]'.format(x) for x in words[0].split()]
                )
            ),
        ),
    )


def no_residual_characters():
    np.debugger.output.clear()
    np.show(':d', 'No Residual Characters')
    with np.Progress(3) as prog:
        np.config(debug_output=False)
        prog.update('AAAA')  # use end='\r'
        prog.update('BBB')
        np.config(debug_output=True)
        prog.update('CCC')  # use end='\n'
    validate_bbcode_output(
        1,  # indicates line of `prog.update('CCC')`
        compose_bbcode_output(
            100,
            '[red]████████████████████████████████████████[/] [red]\\[3/3][/] CCC'
        )
    )


if __name__ == '__main__':
    main()
