import sys, os
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
    
    print("=== ACTUAL ===")
    print("cap.output[0]:", repr(cap.output[0]))
    print("cap.output[1]:", repr(cap.output[1]))
    print()
    
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
    
    print("=== EXPECTED 2 ===")
    print(repr(expected2))
    print()
    
    # 找出区别
    print("=== DIFFERENCE ===")
    actual_lines = cap.output[1].splitlines()
    expected_lines = expected2.splitlines()
    
    for i, (a, e) in enumerate(zip(actual_lines, expected_lines)):
        if a != e:
            print(f"Line {i}:")
            print(f"Actual:  {repr(a)}")
            print(f"Expect:  {repr(e)}")
