import neoprint as np
from pprint import pprint


def main() -> None:
    # np.config(show_source=False, debug_output=True)
    np.config(debug_output=True)

    name = 'Alice'
    age = 20
    city = 'New York'

    np.show('#1', name, age, city, ':n')
    # should print '#1; name = "Alice"; age = 20; city = "New York"'

    np.show('#2', name, len(name), ':n')

    pprint([np.util.strip_ansi_code(x) for x in np.debugger.output])


if __name__ == '__main__':
    main()
