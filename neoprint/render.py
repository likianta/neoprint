import typing as tp

from .config import config


class T:
    ColorCodeScheme = tp.Literal['ansi', 'bbcode', 'plain']
    Color = tp.Literal[
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
    Style = tp.Literal['', 'bold', 'dim', 'italic', 'underline']


# https://chatgpt.com/share/6a17de0b-a134-8321-93d4-3dfdf1e5204d
ANSI_ESCAPE = '\033'
ANSI_RESET = '\033[0m'
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
    *args: tp.Union[
        tp.Tuple[str], tp.Tuple[str, T.Color], tp.Tuple[str, T.Color, T.Style]
    ],
    color_code_scheme: T.ColorCodeScheme = 'plain',
) -> str:
    """
    args: (element, ...)
        element:
            (text,): e.g. ('hello',)
            (text, color): e.g. ('hello', 'red')
            (text, color, style): e.g. ('hello', 'red', 'bold')
    """
    result: tp.List[str] = []
    for element in args:
        if (
            color_code_scheme == 'plain'
            or config.legacy_windows
            or len(element) == 1
        ):
            result.append(element[0])
        else:
            element += ('',)
            # if (
            #     element[1] in ('default', 'bright_black')
            #     and element[2] == 'dim'
            # ):
            #     element = (element[0], 'bright_black', '')

            if color_code_scheme == 'ansi':
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


def translate(bbcode_text: str) -> tp.Iterator[tp.Tuple[str, T.Color, T.Style]]:
    """
    translate bbcode text to ansi colored text.

    for example:
        '[red]hello[/] [green]world[/]' -> (
            ('hello', 'red', ''),
            (' ', 'default', ''),
            ('world', 'green', ''),
        )

    see also `test/bbcode_to_ansi.py`.
    """
    stack = [('default', '')]
    current_text = ''
    i = 0
    length = len(bbcode_text)

    while i < length:
        ch = bbcode_text[i]
        if ch == '\\' and i + 1 < length and bbcode_text[i + 1] == '[':
            current_text += '['
            i += 2
        elif ch == '[':
            end = bbcode_text.find(']', i)
            if end == -1:
                current_text += bbcode_text[i:]
                break
            elif tag := bbcode_text[i + 1 : end]:
                if current_text:
                    yield (  # type: ignore
                        current_text,
                        stack[-1][0],
                        stack[-1][1],
                    )
                    current_text = ''
                if tag == '/':
                    if stack:
                        stack.pop()
                else:
                    new_color = stack[-1][0]
                    new_style = stack[-1][1]
                    valid_tag = True
                    for part in tag.split():
                        if part in ANSI_COLORS:
                            new_color = part
                        elif part in ANSI_STYLES:
                            new_style = part
                        else:
                            # when invalid part found, we treat the tag as plain
                            # text.
                            valid_tag = False
                            break
                    if valid_tag:
                        stack.append((new_color, new_style))
                    else:
                        current_text += bbcode_text[i + 1 : end]
                i = end + 1
            else:
                assert end == i + 1
                current_text += '[]'
                i += 2
        else:
            current_text += ch
            i += 1

    if current_text:
        yield (current_text, stack[-1][0], stack[-1][1])  # type: ignore
