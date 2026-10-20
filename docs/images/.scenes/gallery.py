import neoprint as np

np.show(':d', 'colors')
np.show(
    '[red]red[/] [green]green[/] [yellow]yellow[/] '
    '[blue]blue[/] [magenta]magenta[/] [cyan]cyan[/]',
    ':r',
)
np.show(':d', 'styles')
np.show(
    '[bold]bold[/] [dim]dim[/] [italic]italic[/] '
    '[underline]underline[/]',
    ':r',
)
np.show(':d', 'table')
np.show(':l2', {'Key': 'Value', 'name': 'Alice', 'age': 30})