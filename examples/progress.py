import faker
import neoprint as np
from random import choice
from time import sleep

fk = faker.Faker()

np.show(':d', 'colorful items')
with np.Progress(100, 'none') as prog:
    for _ in range(100):
        prog.update(
            np.Text(
                fk.sentence(),
                choice(('blue', 'cyan', 'green', 'yellow', 'red')),
                choice(('', '', '', '', '', 'dim', 'dim')),
            )
        )
        sleep(0.03)
