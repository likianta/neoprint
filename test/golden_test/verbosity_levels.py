import neoprint as np

np.debug.enabled = True

np.show(':v0', 'NORMAL MESSAGE')
np.show(':v1', 'DEBUG')
np.show(':v2', 'INFO')
np.show(':v3', 'WEAK SUCCESS')
np.show(':v4', 'SUCCESS')
np.show(':v5', 'WEAK WARNING')
np.show(':v6', 'WARNING')
np.show(':v7', 'WEAK ERROR')
np.show(':v8', 'ERROR')
np.show(':v9', 'CRITICAL')


def check(index: int, expected: str) -> None:
    actual = np.debug.output[index]
    assert np.util.ansi_to_bbcode(actual) == expected, (index, expected, actual)


check(0, 'verbosity_levels.py:5   | NORMAL MESSAGE\n')
check(1, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]6  [/]'
    ' [bright_black]|[/] '
    '[bright_black]DEBUG[/]\n'
))
check(2, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]7  [/]'
    ' [bright_black]|[/] '
    '[cyan]INFO[/]\n'
))
check(3, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]8  [/]'
    ' [bright_black]|[/] '
    '[dim green]WEAK SUCCESS[/]\n'
))
check(4, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]9  [/]'
    ' [bright_black]|[/] '
    '[green]SUCCESS[/]\n'
))
check(5, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]10 [/]'
    ' [bright_black]|[/] '
    '[dim yellow]WEAK WARNING[/]\n'
))
check(6, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]11 [/]'
    ' [bright_black]|[/] '
    '[yellow]WARNING[/]\n'
))
check(7, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]12 [/]'
    ' [bright_black]|[/] '
    '[dim red]WEAK ERROR[/]\n'
))
check(8, (
    '[bold blue]verbosity_levels.py[/]'
    '[dim blue]:[/]'
    '[dim blue]13 [/]'
    ' [bright_black]|[/] '
    '[red]ERROR[/]\n'
))
check(9, (
    '[bold red]verbosity_levels.py[/]'
    '[dim red]:[/]'
    '[dim red]14 [/]'
    ' [bright_black]|[/] '
    '[white on red]CRITICAL[/]\n'
))
