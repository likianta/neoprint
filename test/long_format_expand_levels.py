import neoprint as np

np.config(debug_output=True)

# ---------------------------------------------------------------------------
# Test :l0 (disabled) — should output normal single-line format
# ---------------------------------------------------------------------------
np.show(':l0', ['a', 'b', 'c'])
output0 = np.util.strip_ansi(np.debugger.output[-1])
assert output0.rstrip('\n').count('\n') == 0
assert "'a'" in output0 and "'b'" in output0 and "'c'" in output0

# ---------------------------------------------------------------------------
# Test :l1 (= :l) — basic multi-line expand (pprint-like)
# ---------------------------------------------------------------------------
np.show(':l1', ['a', 'b', 'c'])
output1 = np.util.strip_ansi(np.debugger.output[-1])
lines1 = output1.splitlines()
assert len(lines1) > 1
assert lines1[1] == '  ['
assert lines1[2] == '    "a",'
assert lines1[3] == '    "b",'
assert lines1[4] == '    "c",'
assert lines1[-1] == '  ]'

# ---------------------------------------------------------------------------
# Test :l2 — specialized formatting
# Args: Table | Colored string | KV table
# ---------------------------------------------------------------------------
np.show(':l2', [
    ('index', 'name', 'age', 'city'),
    ('1', 'AAA', '20', 'New York'),
    ('2', 'BBB', '22', 'Los Angeles'),
], 'v0.1.0 -> v0.2.0', {'name': 'neoprint', 'version': '0.1.0'})

# Check plain text structure
output2 = np.util.strip_ansi(np.debugger.output[-1])
assert '| index | name | age | city' in output2
assert '| -----' in output2
assert '| 1     | AAA' in output2
assert '| 2     | BBB' in output2
assert 'v0.1.0 -> v0.2.0' in output2
assert '| KEY' in output2
assert '| neoprint' in output2

# Check ANSI colors on the -> string
output2_bb = np.util.ansi_to_bbcode(np.debugger.output[2])
assert '[red]v0.1.0[/] -> [green]v0.2.0[/]' in output2_bb

# ---------------------------------------------------------------------------
# Test :l2 fallback — non-specialized objects use :l1 style
# ---------------------------------------------------------------------------
np.show(':l2', 42, 'plain string')
output3 = np.util.strip_ansi(np.debugger.output[-1])
lines3 = output3.splitlines()
assert '42' in output3
assert 'plain string' in output3