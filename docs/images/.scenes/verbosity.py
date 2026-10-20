import neoprint as np

np.show('[red]error[/] [yellow]warning[/] [green]success[/]', ':r')
np.show(':v1', 'DEBUG message - dim gray')
np.show(':v2', 'INFO message - cyan')
np.show(':v4', 'SUCCESS message - bright green')
np.show(':v6', 'WARNING message - bright yellow')
np.show(':v8', 'ERROR message - bright red')
np.debug('This is a debug message')
np.info('This is an info message')
np.success('This is a success message')
np.warning('This is a warning message')
np.error('This is an error message')