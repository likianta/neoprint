import neoprint as np

names = ['Alice', 'Bob', 'Carol']

with np.Progress(total=len(names)) as prog:
    for name in names:
        prog.update(name)