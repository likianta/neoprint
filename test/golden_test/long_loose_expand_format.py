import neoprint as np
import os

np.config(debug_output=True)

filenames = os.listdir('neoprint')
filenames_rev = filenames[::-1]
np.show(':l', filenames)
np.show(':nl', filenames, filenames_rev)
np.show(':nlv6', filenames)

# ---

output0 = np.util.strip_ansi(np.debugger.output[0])
lines0 = output0.splitlines()
assert len(lines0) > 1
assert lines0[0] == 'long_loose_expand_format.py:8   | '
assert lines0[1] == '  ['
assert lines0[2] == '    "capture.py",'
assert lines0[3] == '    "config.py",'
...
assert lines0[-1] == '  ]'

output1 = np.util.strip_ansi(np.debugger.output[1])
lines1 = output1.splitlines()
assert lines1[0] == 'long_loose_expand_format.py:9   | '
assert lines1[1] == '  filenames = ['
flag = 'INIT'
for line in lines1[2:]:
    if flag == 'INIT':
        if line.lstrip().startswith(']'):
            assert line == '  ],'
            flag = 'CHECK_REV_START'
        continue
    if flag == 'CHECK_REV_START':
        assert line == '  filenames_rev = ['
        break

output2 = np.util.ansi_to_bbcode(np.debugger.output[2])
lines2 = output2.splitlines()
assert lines2[0] == (
    '[bold blue]long_loose_expand_format.py[/]'
    '[dim blue]:[/]'
    '[dim blue]10 [/]'
    ' [bright_black]|[/] '
)
assert lines2[1] == '  [yellow]filenames = \\[[/]'
assert lines2[2] == '    [yellow]"capture.py",[/]'
assert lines2[-1] == '  [yellow]][/]'
