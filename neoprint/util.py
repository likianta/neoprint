import re

_ansi_color_to_bbcode = {
    '30': 'black',
    '31': 'red',
    '32': 'green',
    '33': 'yellow',
    '34': 'blue',
    '35': 'magenta',
    '36': 'cyan',
    '37': 'white',
    '90': 'bright_black',
    '91': 'red',
    '92': 'green',
    '93': 'yellow',
    '94': 'blue',
    '95': 'magenta',
    '96': 'cyan',
    '97': 'white',
}

_ansi_bgcolor_to_bbcode = {
    '40': 'black',
    '41': 'red',
    '42': 'green',
    '43': 'yellow',
    '44': 'blue',
    '45': 'magenta',
    '46': 'cyan',
    '47': 'white',
}


def ansi_to_bbcode(text):
    """将 ANSI 转义序列转换为 bbcode 格式"""
    result = []
    i = 0
    n = len(text)
    open_tags = []

    while i < n:
        if i + 1 < n and text[i] in '\x1b\x033' and text[i + 1] == '[':
            ansi_start = i
            i += 2
            m_pos = text.find('m', i)
            if m_pos != -1:
                codes = text[i:m_pos].split(';')
                i = m_pos + 1

                if len(codes) == 1 and codes[0] == '0':
                    for _ in range(len(open_tags)):
                        result.append('[/]')
                    open_tags.clear()
                    continue

                style = ''
                color = None
                bgcolor = None
                for code in codes:
                    if code == '1':
                        style = 'bold '
                    elif code == '2':
                        style = 'dim '
                    elif code in _ansi_color_to_bbcode:
                        color = _ansi_color_to_bbcode[code]
                    elif code in _ansi_bgcolor_to_bbcode:
                        bgcolor = _ansi_bgcolor_to_bbcode[code]

                if color or bgcolor:
                    tag_parts = []
                    if style:
                        tag_parts.append(style.strip())
                    if color:
                        tag_parts.append(color)
                    if bgcolor:
                        tag_parts.append(f'on {bgcolor}')
                    tag = f'[{" ".join(tag_parts)}]'
                    open_tags.append(tag)
                    result.append(tag)
            else:
                result.append(text[ansi_start:i])
        else:
            if text[i] == '[':
                result.append('\\[')
            else:
                result.append(text[i])
            i += 1

    for _ in range(len(open_tags)):
        result.append('[/]')

    return ''.join(result)


def strip_ansi(text: str) -> str:
    pattern = r'\033\[[0-9;]*m'
    return re.sub(pattern, '', text)


__all__ = ['ansi_to_bbcode', 'strip_ansi']
