import re
import typing as tp

from . import render

# Reverse mapping from ANSI codes to color/style names
_ANSI_CODE_TO_COLOR = {
    '30': 'black',
    '31': 'red',
    '32': 'green',
    '33': 'yellow',
    '34': 'blue',
    '35': 'magenta',
    '36': 'cyan',
    '37': 'white',
    '39': 'default',
    '90': 'bright_black',
    '91': 'bright_red',
    '92': 'bright_green',
    '93': 'bright_yellow',
    '94': 'bright_blue',
    '95': 'bright_magenta',
    '96': 'bright_cyan',
    '97': 'bright_white',
}
_ANSI_CODE_TO_STYLE = {'1': 'bold', '2': 'dim', '3': 'italic', '4': 'underline'}


def ansi_to_bbcode(s: str) -> str:
    """
    convert ansi escape codes to bbcode.
    for example: '\\x1b[31mhello\\x1b[0m' -> '[red]hello[/]'
    """
    result: tp.List[str] = []
    current_color = 'default'
    current_style = ''
    last_end = 0

    for match in re.finditer(r'\x1b\[([0-9;]*)m', s):
        codes = match.group(1).split(';') if match.group(1) else ['0']
        start = match.start()
        text = s[last_end:start]

        if text:
            if current_style:
                result.append(
                    '[{} {}]{}[/]'.format(
                        current_style, current_color, text.replace('[', '\\[')
                    )
                )
            else:
                result.append(
                    '[{}]{}[/]'.format(current_color, text.replace('[', '\\['))
                )

        for code in codes:
            if code == '0':
                current_color = 'default'
                current_style = ''
            elif code in _ANSI_CODE_TO_COLOR:
                current_color = _ANSI_CODE_TO_COLOR[code]
            elif code in _ANSI_CODE_TO_STYLE:
                current_style = _ANSI_CODE_TO_STYLE[code]

        last_end = match.end()

    remaining = s[last_end:]
    if remaining:
        if current_style:
            result.append(
                '[{} {}]{}[/]'.format(
                    current_style, current_color, remaining.replace('[', '\\[')
                )
            )
        else:
            result.append(
                '[{}]{}[/]'.format(current_color, remaining.replace('[', '\\['))
            )

    return ''.join(result)


def bbcode_to_ansi(s: str) -> str:
    """
    convert bbcode to ansi escape codes.
    """
    return render.render(*render.translate(s), color_code_scheme='ansi')


def strip_ansi_code(s: str) -> str:
    return re.sub(r'\x1b\[.*?m', '', s)
