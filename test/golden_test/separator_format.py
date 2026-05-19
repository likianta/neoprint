import neoprint as np

np.config(show_source=True, show_funcname=False)

text = np.format('hello', 'world', color_code_scheme='bbcode')
print(text)
assert text == (
    '[blue]separator_format.py[/]'
    '[dim blue]:[/]'
    '[dim blue]5  [/]'
    ' [bright_black]|[/] '
    'hello'
    '[bright_black];[/] '
    'world'
)
