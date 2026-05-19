import neoprint as np
import traceback

def foo():
    np.show(':i', 'foo level')
    bar()

def bar():
    np.show(':p1i', 'showing parent from bar')
    np.show(':p2i', 'showing grandparent from bar')
    baz()

def baz():
    np.show(':p2i', 'showing grandparent from baz')
    np.show(':p3i', 'showing great-grandparent from baz')

print("=== Testing :p mark ===")
np.debug.enabled = True
foo()

print("\n=== Testing very deep :p (should use <unknown> fallback) ===")
np.show(':p100i', 'Showing very deep stack')

print("\nTest completed!")
