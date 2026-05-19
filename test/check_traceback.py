import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import traceback

try:
    1 / 0
except ZeroDivisionError as e:
    lines = traceback.format_exception(type(e), e, e.__traceback__)
    for i, line in enumerate(lines):
        print(f"Line {i}: {repr(line)}")
