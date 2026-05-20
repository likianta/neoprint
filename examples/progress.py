import faker
import neoprint as np
from random import choice
from time import sleep

fk = faker.Faker()

with np.Progress(100, 'none') as prog:
    for _ in range(100):
        prog.update(fk.sentence(), choice((':v2', ':v4', ':v6', ':v8')))
        sleep(0.03)
