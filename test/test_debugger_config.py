import neoprint as np

print("Testing config debug_output:")

# Test using np.config(debug_output=True)
np.config(debug_output=True)
np.debugger.output.clear()

np.show("hello from config test 1")

assert len(np.debugger.output) == 1
print("✓ np.config(debug_output=True) works")

# Test using np.config(debug_output=False)
np.config(debug_output=False)
np.show("this won't be captured")

assert len(np.debugger.output) == 1
print("✓ np.config(debug_output=False) works")

# Test using np.debugger.enabled directly
np.debugger.enabled = True
np.debugger.output.clear()
np.info("this will be captured")
assert len(np.debugger.output) == 1
print("✓ np.debugger.enabled works")

# Test aliases all work with correct line numbers
print("\nTesting aliases:")
from neoprint import print as np_print, debug, info, success, warning, error

np_print("test print")
debug("test debug")
info("test info")
success("test success")
warning("test warning")
error("test error")

try:
    1 / 0
except ZeroDivisionError as e:
    error(e, ":e2")
