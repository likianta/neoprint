import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neoprint as np


def main() -> None:
    np.config(show_source=False, show_funcname=False)

    name = 'Alice'
    age = 20
    city = 'New York'

    np.show('#1', name, age, city, markup=':v')

    with np.capture_output(color_code_scheme='none') as cap:
        np.show('#2', name, age, city, markup=':v')
        print('=== ACTUAL ===')
        print(repr(cap.output[0]))
        print('\n=== EXPECTED ===')
        print(repr('#2; name = "Alice"; age = 20; city = "New York"'))
        assert (
            cap.output[0] == '#2; name = "Alice"; age = 20; city = "New York"'
        )


if __name__ == '__main__':
    main()
