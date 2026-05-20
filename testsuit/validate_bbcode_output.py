import neoprint as np

def expected_bbcode_output(lineno: int, *body_parts):
    assert lineno < 1000
    frame_info = np.util.get_caller_frame(1)
    return (
        '[bold blue]{}[/]'.format(frame_info.filename)
        + '[dim blue]:[/]'
        + '[dim blue]{:<3}[/]'.format(lineno)
        + ' [bright_black]|[/] '
        + '[bright_black];[/] '.join(body_parts)
        + '\n'
    )

def validate_bbcode_output(dbg_index: int, lineno, expected: str):
    actual = np.util.ansi_to_bbcode(np.debugger.output[dbg_index])
    assert actual == expected, np.format(expected, actual, ':nlv8p')
