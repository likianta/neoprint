import sys
import os

# Set path
test_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_script_dir)
sys.path.insert(0, project_root)

import neoprint as np
from textwrap import dedent

np.show('format exception test')

try:
    1 / 0
except ZeroDivisionError as e:
    with np.capture_output() as cap:
        np.show(e, ':c8')
        np.show(e, ':lc8')
    
    print('Asserting cap.output[0]:')
    expected1 = 'format_exception.py:12  >  <module>  >  division by zero'
    actual1 = cap.output[0]
    print(f'Expected: {repr(expected1)}')
    print(f'Actual  : {repr(actual1)}')
    print(f'Equal? {actual1 == expected1}')
    
    print('\nAsserting cap.output[1]:')
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
    print(f'Expected: {repr(expected2)}')
    print(f'Actual  : {repr(cap.output[1])}')
    print(f'Equal? {cap.output[1] == expected2}')
    
    if cap.output[1] != expected2:
        print('\n--- Expected ---')
        print(repr(expected2))
        print('\n--- Actual ---')
        print(repr(cap.output[1]))
