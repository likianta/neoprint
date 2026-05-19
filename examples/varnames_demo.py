import neoprint as np


def main():
    name = 'Alice'
    age = 30
    city = 'New York'

    print('Using get_body_string with :n markup (show_varnames):')
    result = np.get_body_string(name, age, city, markup=':n')
    print(result)
    print()

    print('Without markup (just values):')
    result = np.get_body_string(name, age, city)
    print(result)
    print()

    print('With verbosity level :v4 (success):')
    result = np.get_body_string(name, age, city, markup=':v4')
    print(result)
    print()

    print('With verbosity level :v6 (warning):')
    result = np.get_body_string(name, age, city, markup=':v6')
    print(result)


if __name__ == '__main__':
    main()
