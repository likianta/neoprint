from .console import strip_ansi

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
                for code in codes:
                    if code == '1':
                        style = 'bold '
                    elif code == '2':
                        style = 'dim '
                    elif code in _ansi_color_to_bbcode:
                        color = _ansi_color_to_bbcode[code]

                if color:
                    tag = f'[{style}{color}]'
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


__all__ = ['ansi_to_bbcode', 'strip_ansi']
