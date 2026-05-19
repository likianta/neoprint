import neoprint as np


def main() -> None:
    np.config(show_source=False, show_funcname=False)
    #   show_source=False: do not show `filepath:lineno` part.
    #   show_funcname=False: do not show `funcname()` part.

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


if __name__ == '__main__':
    main()
