from neoprint.render import translate

# classic
result = tuple(translate('[red]hello[/] [green]world[/]'))
assert result == (
    ('hello', 'red', ''),
    (' ', 'default', ''),
    ('world', 'green', ''),
)

# style
result = tuple(translate('[red bold]hello[/]'))
assert result == (('hello', 'red', 'bold'),)

# nested
result = tuple(translate('[red bold]aaa [green]bbb[/] [italic]ccc[/] ddd[/]'))
assert result == (
    ('aaa ', 'red', 'bold'),
    ('bbb', 'green', 'bold'),
    (' ', 'red', 'bold'),
    ('ccc', 'red', 'italic'),
    (' ddd', 'red', 'bold'),
)
