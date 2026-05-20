import neoprint as np

np.debugger.enabled = True

np.show('hello', 'world', ':v4')
assert np.util.ansi_to_bbcode(np.debugger.output[-1]) == (
    '[bold blue]debug_show.py[/]'
    '[dim blue]:[/]'
    '[dim blue]5  [/]'
    ' [bright_black]|[/] '
    '[green]hello[/]'
    '[bright_black];[/] '
    '[green]world[/]'
    '\n'
)

np.show('foo', 'bar', ':i')
assert np.util.ansi_to_bbcode(np.debugger.output[-1]) == (
    '[bold blue]debug_show.py[/]'
    '[dim blue]:[/]'
    '[dim blue]17 [/]'
    ' [bright_black]|[/] '
    '[red]\\[1][/] '
    'foo'
    '[bright_black];[/] '
    'bar'
    '\n'
)

np.show('foo', 'bar', 'baz')
assert np.util.ansi_to_bbcode(np.debugger.output[-1]) == (
    '[bold blue]debug_show.py[/]'
    '[dim blue]:[/]'
    '[dim blue]30 [/]'
    ' [bright_black]|[/] '
    'foo'
    '[bright_black];[/] '
    'bar'
    '[bright_black];[/] '
    'baz'
    '\n'
)
