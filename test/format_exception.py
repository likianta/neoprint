import neoprint as np
from textwrap import dedent

np.show('format exception test')

try:
    1 / 0
except ZeroDivisionError as e:
    with np.capture_output() as cap:
        np.show(e, ':v8')
        np.show(e, ':lv8')

    assert cap.output[0] == 'format_exception.py:10   | division by zero'
    
    expected_traceback = dedent(
        """
        format_exception.py:11   | 
            Traceback (most recent call last):
                File "C:\\Likianta\\workspace\\dev.master.likianta\\neoprint\\test\\format_exception.py", line 7, in <module>
                    1 / 0
                    ~~^~~
            ZeroDivisionError: division by zero
        """
    ).strip()
    assert cap.output[1] == '\n' + expected_traceback + '\n'

print('✅ All tests passed!')
