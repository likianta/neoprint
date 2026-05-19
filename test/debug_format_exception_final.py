import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neoprint as np

try:
    1 / 0
except ZeroDivisionError as e:
    with np.capture_output() as cap:
        np.show(e, ':c8')
        np.show(e, ':lc8')
    
    print("=== Output length: %d ===" % len(cap.output))
    for i, out in enumerate(cap.output):
        print("=== Output %d ===" % i)
        print(repr(out))
