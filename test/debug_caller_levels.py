import neoprint as np
from neoprint.show import _get_caller_frame

print("Testing _get_caller_frame levels:")

for i in range(0, 10):
    f = _get_caller_frame(i)
    print(f"  level {i}: {f.filename}:{f.lineno} in {f.funcname}")

print("\nCalling np.debug directly:")
np.debug("test 1")

print("\nCalling via __debug import:")
from neoprint import debug
debug("test 2")
