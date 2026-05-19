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
    
    assert cap.output[0] == 'format_exception.py:15  >  <module>  >  division by zero'
    
    expected_traceback = dedent(
        """
        format_exception.py:17  >  <module>  >
            Traceback (most recent call last):
                File "C:\\Likianta\\workspace\\dev.master.likianta\\neoprint\\test\\format_exception.py", line 11, in <module>
                    1 / 0
                    ~~^~~
            ZeroDivisionError: division by zero
        """
    )
    print("=== Actual ===\n" + repr(cap.output[1]))
    print("\n=== Expected ===\n" + repr(expected_traceback))
    assert cap.output[1] == expected_traceback, "Traceback didn't match!"
    
    print("\n✅ All tests passed!")
