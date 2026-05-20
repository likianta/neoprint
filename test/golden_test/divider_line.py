import neoprint as np

np.config(debug_output=True)

# test no text, one text, multi texts
np.show(':d')
np.show(':d', 'AAA')
np.show(':d', 'AAA', 'BBB')

# test different levels
np.show(':d0', 'CCC')
np.show(':d1', 'DDD')
np.show(':d2', 'EEE')

# test with color
np.show(':dv6', 'FFF', 'GGG')

# other markup combinations
name = 'Alice'
np.show(':ndiv2', 'HHH', name, 'OK')

# ---

output_0 = np.util.ansi_to_bbcode(np.debugger.output[0])
console_width = np.console.get_console_width()
div_char_count = output_0.count('─')
assert output_0 == (
    '[bold blue]divider_line.py[/]'
    '[dim blue]:[/]'
    '[dim blue]6  [/]'
    ' [bright_black]|[/] '
    '[bright_black]{}[/]'.format('─' * div_char_count)
    + '\n'
)
# assert len(np.util.strip_ansi(output_0)[:-1]) == console_width

output_bbb = np.util.ansi_to_bbcode(np.debugger.output[2])
assert '─ AAA[bright_black];[/] BBB ─' in output_bbb

output_ccc = np.util.strip_ansi(np.debugger.output[3])
assert output_ccc == 'divider_line.py:11  | CCC\n'

output_fff = np.util.ansi_to_bbcode(np.debugger.output[6])
assert (
    '[yellow]───' in output_fff
    and '───[/] [yellow]FFF[/][bright_black];[/] [yellow]GGG[/] [yellow]───' 
    in output_fff
)

output_hhh = np.util.strip_ansi(np.debugger.output[7])
div_char_count = output_hhh.count('─')
assert div_char_count % 2 == 0
assert (
    output_hhh
    == 'divider_line.py:20  | [1] {} HHH; name = "Alice"; OK {}\n'.format(
        '─' * int(div_char_count / 2),
        '─' * int(div_char_count / 2),
    )
)
