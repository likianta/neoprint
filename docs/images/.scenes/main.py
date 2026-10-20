import neoprint as np

np.show('[bold cyan]Neoprint[/] - expressive console output', ':r')
np.show(':d')

name = 'Alice'
age = 30
city = 'New York'
np.show(name, age, city, ':n')

np.show(':v2', 'INFO message - cyan')
np.show(':v4', 'SUCCESS message - bright green')
np.show(':v6', 'WARNING message - bright yellow')
np.show(':v8', 'ERROR message - bright red')

np.show(':i2', 'indexed item')
np.show(':d')
np.show('[green]everything in one place[/]', ':r')