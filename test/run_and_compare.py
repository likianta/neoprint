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
    
    print('=== Output 0 ===')
    print(repr(cap.output[0]))
    
    print('\n=== Output 1 ===')
    print(repr(cap.output[1]))
    
    print('\n=== Expected 2 ===')
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
    
    print(f"\nAre they equal? {cap.output[1] == expected2}")
