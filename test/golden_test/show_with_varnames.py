import neoprint as np


def main() -> None:
    np.config(show_source=False, show_funcname=False, debug_output=True)

    name = 'Alice'
    age = 20
    city = 'New York'

    np.show('#1', name, age, city, markup=':n')
    # should print '#1; name = "Alice"; age = 20; city = "New York"'

    with np.capture_output(color_code_scheme='none') as cap:
        #   @contextmanager
        #   def capture_output(
        #       color_code_scheme: Literal['none', 'ascii', 'bbcode'] = 'none'
        #   ): ...
        np.show('#2', name, age, city, markup=':n')
        assert (
            cap.output[0] == '#2; name = "Alice"; age = 20; city = "New York"'
        )
    
    np.info('#3', name, age, city, 'OK', ':n')
    assert np.util.ansi_to_bbcode(np.debugger.output[-1]) == (
        '[cyan]#3[/]'
        '[bright_black];[/] '
        '[cyan]name = "Alice"[/]'
        '[bright_black];[/] '
        '[cyan]age = 20[/]'
        '[bright_black];[/] '
        '[cyan]city = "New York"[/]'
        '[bright_black];[/] '
        '[cyan]OK[/]'
        '\n'
    )


if __name__ == '__main__':
    main()
