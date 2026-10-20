import neoprint as np

with np.Progress(total=100) as prog:
    for i in range(68):
        prog.update('Processing item {}'.format(i + 1))