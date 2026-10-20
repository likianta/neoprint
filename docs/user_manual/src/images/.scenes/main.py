import neoprint as np

name = 'Alice'
age = 30
np.show(name, age, ':n')

np.show(
    '[bold cyan]colors[/], [green]varnames[/], '
    '[yellow]progress bars[/]',
    ':r',
)
np.show(':v4', 'SUCCESS: pretty output, one dependency')
np.show(':d2', 'ready')