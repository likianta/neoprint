import typing as t


class T:
    CodeScheme = t.Literal['ansi', 'bbcode', 'none']
    Color = t.Literal[
        # '',
        'black',
        'blue',
        'bright_black',
        'bright_blue',
        'bright_cyan',
        'bright_green',
        'bright_magenta',
        'bright_red',
        'bright_yellow',
        'cyan',
        'default',
        'green',
        'magenta',
        'red',
        'white',
        'yellow',
    ]
    Style = t.Literal['', 'bold', 'dim', 'italic', 'underline']


# https://chatgpt.com/share/6a17de0b-a134-8321-93d4-3dfdf1e5204d
ANSI_ESCAPE = '\033'
ANSI_RESET = ANSI_ESCAPE + '[0m'
ANSI_COLORS = {
    'black': '30',
    'red': '31',
    'green': '32',
    'yellow': '33',
    'blue': '34',
    'magenta': '35',
    'cyan': '36',
    'white': '37',
    'default': '39',
    'bright_black': '90',
    'bright_red': '91',
    'bright_green': '92',
    'bright_yellow': '93',
    'bright_blue': '94',
    'bright_magenta': '95',
    'bright_cyan': '96',
    'bright_white': '97',
}
ANSI_STYLES = {
    # 'reset': '0',
    'bold': '1',
    'dim': '2',
    'italic': '3',
    'underline': '4',
}


def render(
    *args: t.Union[
        t.Tuple[str], t.Tuple[str, T.Color], t.Tuple[str, T.Color, T.Style]
    ],
    code_scheme: T.CodeScheme = 'none',
) -> str:
    """
    args: (element, ...)
        element:
            (text,): e.g. ('hello',)
            (text, color): e.g. ('hello', 'red')
            (text, color, style): e.g. ('hello', 'red', 'bold')
    """
    result: t.List[str] = []
    for element in args:
        if code_scheme == 'none' or len(element) == 1:
            result.append(element[0])
        else:
            element += ('',)
            # if (
            #     element[1] in ('default', 'bright_black')
            #     and element[2] == 'dim'
            # ):
            #     element = (element[0], 'bright_black', '')

            if code_scheme == 'ansi':
                if element[2] == '':
                    result.append(
                        '{}[{}m{}{}'.format(
                            ANSI_ESCAPE,
                            ANSI_COLORS[element[1]],
                            element[0],
                            ANSI_RESET,
                        )
                    )
                else:
                    result.append(
                        '{}[{};{}m{}{}'.format(
                            ANSI_ESCAPE,
                            ANSI_STYLES[element[2]],
                            ANSI_COLORS[element[1]],
                            element[0],
                            ANSI_RESET,
                        )
                    )
            else:
                if element[2] == '':
                    result.append(
                        '[{}]{}[/]'.format(
                            element[1], element[0].replace('[', '\\[')
                        )
                    )
                else:
                    result.append(
                        '[{} {}]{}[/]'.format(
                            element[2],
                            element[1],
                            element[0].replace('[', '\\['),
                        )
                    )
    return ''.join(result)
