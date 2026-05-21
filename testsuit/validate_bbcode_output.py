import neoprint as np


def compose_bbcode_output(lineno: int, *body_parts: str) -> str:
    assert lineno < 1000
    frame_info = np.frame_info.get_caller_frame()
    return (
        '[bold blue]{}[/]'.format(frame_info.filename)
        + '[dim blue]:[/]'
        + '[dim blue]{:<3}[/]'.format(lineno)
        + ' [bright_black]|[/] '
        + '[bright_black];[/] '.join(body_parts)
        + '\n'
    )


def validate_bbcode_output(dbg_index: int, *args) -> None:
    if len(args) == 1:
        expected = args[0]
    elif len(args) == 2:
        _, expected = args
    else:
        raise TypeError(
            f'validate_bbcode_output() takes 2 or 3 positional arguments '
            f'but {len(args) + 1} were given'
        )
    actual = np.util.ansi_to_bbcode(np.debugger.output[dbg_index])
    assert actual == expected, np.format(expected, actual, ':nlv8p')