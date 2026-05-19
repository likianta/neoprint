import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neoprint as np
from textwrap import dedent

np.show('format exception test')

try:
    1 / 0
except ZeroDivisionError as e:
    with np.capture_output() as cap:
        np.show(e, ':c8')
        np.show(e, ':lc8')
    
    print("=== CHECK CAP.OUTPUT ===")
    print("LEN:", len(cap.output))
    for i, output in enumerate(cap.output):
        print(f"Index {i}: {repr(output)}")
    
    print()
    print("=== EXPECTED 1 ===")
    print(repr('format_exception.py:12  >  <module>  >  division by zero'))
    print()
    print("=== EXPECTED 2 ===")
    expected2 = dedent(
        """
        format_exception.py:14  >  <module>  >
            Traceback (most recent call last):
                File "C:\\Likianta\\workspace\\dev.master.likianta\\neoprint\\test\\format_exception.py", line 8, in <module>
                    1 / 0
                    ~~^~~
            ZeroDivisionError: division by zero
        """
    )
    print(repr(expected2))
