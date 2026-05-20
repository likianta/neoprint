import typing as t


class T:
    ColorCodeScheme = t.Literal['ansi', 'bbcode', 'none']


class TextObject:
    # type: t.Literal[
    #     'filename', 
    #     'line_separator', 
    #     'line_number',
    #     'whitespace',
    #     'function_separator',
    #     'function_name',
    #     'message_separator',
    #     'message', 
    #     'markup',
    # ]
    # data: str

    def __init__(self, data: t.Any):
        self.data = data

    def render(self, color_code_scheme: T.ColorCodeScheme = 'none'):
        raise NotImplementedError



class Filename(TextObject):
    def render(self, color_code_scheme: T.ColorCodeScheme = 'none'):
        if color_code_scheme == 'none':
            return self.data
        elif color_code_scheme == 'ansi':
            ...
        elif color_code_scheme == 'bbcode':
            return f'[bold blue]{self.data}[/]'


class LineSeparator(TextObject):
    def __init__(self, character: str = ':'):
        self.data = character

    def render(self, color_code_scheme: T.ColorCodeScheme = 'none'):
        if color_code_scheme == 'none':
            return self.data
        elif color_code_scheme == 'ansi':
            ...
        elif color_code_scheme == 'bbcode':
            return f'[dim blue]{self.data}[/]'


class LineNumber(TextObject):
    def __init__(self, number: int):
        self.data = str(number)

    def render(self, color_code_scheme: T.ColorCodeScheme = 'none'):
        if color_code_scheme == 'none':
            return self.data
        elif color_code_scheme == 'ansi':
            ...
        elif color_code_scheme == 'bbcode':
            return f'[dim blue]{self._pad(self.data)}[/]'

    def _pad(self, text: str, width: int = 3):
        return text.ljust(width)


class Whitespace(TextObject):
    def __init__(self, count: int = 1):
        self.data = ' ' * count

    def render(self, color_code_scheme: T.ColorCodeScheme = 'none'):
        return self.data


class FunctionSeparator(TextObject):
    def __init__(self, character: str = '|'):
        self.data = character

    def render(self, color_code_scheme: T.ColorCodeScheme = 'none'):
        if color_code_scheme == 'none':
            return self.data
        elif color_code_scheme == 'ansi':
            ...
        elif color_code_scheme == 'bbcode':
            return f'[bright_black]{self.data}[/]'

...
