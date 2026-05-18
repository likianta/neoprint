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

    text = np.format('hello', 'world', markup=':c4', color_code_scheme='bbcode')
    # print(text)
    assert text == '[green]hello[/][bright_black]; [/][green]world[/]'


if __name__ == '__main__':
    main()
