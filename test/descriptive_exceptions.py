import neoprint as np
try:
    1 / 0
except ZeroDivisionError as e:
    np.error(e)
    np.exception(e)
