import neoprint as np

try:
    1 / 0
except ZeroDivisionError as e:
    np.show(e, ':v8')
    np.show(':d')
    np.show(e, ':lv8')
