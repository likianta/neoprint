import neoprint as np

try:
    result = 1 / 0
except ZeroDivisionError:
    np.show(':e')