import neoprint as np
from testsuit import validate_bbcode_output

np.config(debug_output=True)

np.show(':v2', ':d means divider line')
np.show(':v4', 'first markup take priority over the last', ':v8')
np.show(':v6', 'markup=... take priority over others', ':v8', markup=':v4')
np.show(':v2v4v6', 'for duplicate markups, the last one effects')
np.show(':v8:', '":v8:" is not a valid markup')

validate_bbcode_output(0, 6, (
    '[bold blue]invalid_markups.py[/]'
    '[dim blue]:[/]'
    '[dim blue]6  [/]'
    ' [bright_black]|[/] '
    '[cyan]:d means divider line[/]'
    '\n'
))
validate_bbcode_output(1, 7, (
    '[bold blue]invalid_markups.py[/]'
    '[dim blue]:[/]'
    '[dim blue]7  [/]'
    ' [bright_black]|[/] '
    '[green]first markup take priority over the last[/]'
    '[bright_black];[/] '
    '[green]:v8[/]'
    '\n'
))
validate_bbcode_output(2, 8, (
    '[bold blue]invalid_markups.py[/]'
    '[dim blue]:[/]'
    '[dim blue]8  [/]'
    ' [bright_black]|[/] '
    '[green]:v6[/]'
    '[bright_black];[/] '
    '[green]markup=... take priority over others[/]'
    '[bright_black];[/] '
    '[green]:v8[/]'
    '\n'
))
validate_bbcode_output(4, 10, (
    '[bold blue]invalid_markups.py[/]'
    '[dim blue]:[/]'
    '[dim blue]10 [/]'
    ' [bright_black]|[/] '
    ':v8:'
    '[bright_black];[/] '
    '":v8:" is not a valid markup'
    '\n'
))
