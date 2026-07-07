from dataclasses import dataclass
from pprint import pprint  # noqa

import neoprint as np


def main() -> None:
    # np.config(show_source=False, debug_output=True)
    np.config(debug_output=True)

    name = 'Alice'
    age = 20
    city = 'New York'

    np.show(name, age, city, ':ni')
    np.show(name, age, city, ':nvi')
    np.show(name, len(name), ':ni')

    person = Person(name, age, city)
    np.show(person.name, person.age, person.city, ':ni')

    # pprint([np.util.strip_ansi_code(x) for x in np.debugger.output])


@dataclass
class Person:
    name: str
    age: int
    city: str


if __name__ == '__main__':
    main()
