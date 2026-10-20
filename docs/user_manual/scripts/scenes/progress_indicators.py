import neoprint as np

with np.Progress(
    total=100, indicator_style='decimal', color='green'
) as p:
    for i in range(42):
        p.update()