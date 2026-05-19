import neoprint as np


def main() -> None:
    np.config(show_source=False, show_funcname=False)
    #   show_source=False: do not show `filepath:lineno` part.
    #   show_funcname=False: do not show `funcname()` part.

    text = np.format('hello', 'world', color_code_scheme='none')
    #   np.format(
    #       *args,
    #       markup: str = '',
    #       color_code_scheme: Literal['none', 'ascii', 'bbcode'] = 'none',
    #       ...
    #   )
    # print(text)
    assert text == 'hello; world'

    text = np.format('hello', 'world', markup=':v4', color_code_scheme='bbcode')
    # print(text)
    assert text == '[green]hello[/][bright_black];[/] [green]world[/]'

    name = 'Alice'
    age = 20
    city = 'New York'
    text = np.format(name, age, city, markup=':n', color_code_scheme='none')
    # print(text)
    assert text == 'name = "Alice"; age = 20; city = "New York"'

    text = np.format(name, age, city, markup=':n', color_code_scheme='bbcode')
    # print(text)
    assert text == (
        'name = "Alice"'
        '[bright_black];[/] '
        'age = 20'
        '[bright_black];[/] '
        'city = "New York"'
    )

    # --------------------------------------------------------------------------

    with np.capture_output('none') as cap:
        np.show('hello', 'world', ':v4')
    assert cap.output[0] == 'hello; world'
    
    with np.capture_output('bbcode') as cap:
        np.show('hello', 'world', ':v4')
    assert cap.output[0] == '[green]hello[/][bright_black];[/] [green]world[/]'
    
    with np.capture_output('ascii') as cap:
        np.show('hello', 'world', ':v4')
    assert cap.output[0] == r'\x1b[0;92mhello\x1b[0m\x1b[90m;\x1b[0m \x1b[0;92mworld\x1b[0m'


if __name__ == '__main__':
    main()
