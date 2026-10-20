import neoprint as np
from random import randint
from time import sleep


def main():
    np.show(':v0', 'DEBUG message (dim default)')
    np.show(':v1', 'NEGATIVE INFO (magenta)')
    np.show(':v2', 'INFO (cyan)')
    np.show(':v3', 'WEAK SUCCESS (dim green)')
    np.show(':v4', 'SUCCESS (bright green)')
    np.show(':v5', 'WEAK WARNING (dim yellow)')
    np.show(':v6', 'WARNING (bright yellow)')
    np.show(':v7', 'WEAK ERROR (dim red)')
    np.show(':v8', 'ERROR (bright red)')

    name = 'Likianta'
    mail = 'likianta@foxmail.com'
    np.show('Hello', name, mail, ':v2n')

    sleep(randint(80, 500) * 1e-3)
    np.show(':d')
    np.show(
        ':r2t',
        {
            'Filename': 'hello_world.py',
            'Line count': 34,
            'Author': 'Likianta (likianta@foxmail.com)',
        },
    )


if __name__ == '__main__':
    main()
