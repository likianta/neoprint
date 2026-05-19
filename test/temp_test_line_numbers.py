import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neoprint as np

np.show('format exception test')

try:
    1 / 0
except ZeroDivisionError as e:
    with np.capture_output() as cap:
        np.show(e, ':c8')
        np.show(e, ':lc8')
    
    print("=== CAPTURED OUTPUT ===")
    for i, out in enumerate(cap.output):
        print(f"Output {i}: {repr(out)}")
