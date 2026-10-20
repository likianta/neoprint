import neoprint as np

try:
    result = 1 / 0
except ZeroDivisionError as e:
    np.show(e, ':e2')