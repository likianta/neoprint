import io
import os
import re
import sys
import tempfile
import typing as tp
from contextlib import contextmanager
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax
from rich.terminal_theme import TerminalTheme
from rich.text import Text

from .rasterize import apply_style
from .rasterize import svg_to_png
from .theme import ThemeSpec
from .theme import resolve_theme
from ..config import config as _config
from ..console import legacy_rich_console
from ..console import rich_console

_ERASE_LINE = re.compile(r'\x1b\[\d*K')
_OTHER_CSI = re.compile(r'\x1b\[\?[0-9;]*[a-zA-Z]')


class Termshot:
    """
    Record console output as an svg image, then rasterize it to png.

    The class is a context manager: everything printed inside the `with`
    block is captured, including plain `print()` and `neoprint.show()`.

    Usage:
        shot = np.termshot(
            title='Neoprint demo',
            command='python main.py hello',
            theme='catppuccin-mocha',
        )
        with shot:
            np.show(name, age, ':n')
        shot.save_png('demo.png')

    See also `neoprint.termshot()`.
    """

    def __init__(
        self,
        *,
        title: str = '',
        command: str = '',
        width: int = 100,
        theme: tp.Union[str, TerminalTheme, None] = None,
        background: tp.Optional[str] = None,
        foreground: tp.Optional[str] = None,
        syntax_theme: tp.Optional[str] = None,
        font: tp.Union[str, tp.Sequence[str], None] = None,
        font_size: int = 20,
        line_height: tp.Optional[float] = None,
        ligatures: bool = True,
        scale: int = 2,
        window_title: str = 'neoprint',
        prompt: str = '$',
    ) -> None:
        """
        params:
            title: a centered, bold line printed at the top.
            command: a shell command line printed below the title, e.g.
                "python main.py hello". the leading prompt is added for you.
            width: the terminal width (in characters) of the recorded image.
            theme: None or 'default' for rich's palette, 'catppuccin' or
                'catppuccin-<flavor>' for a catppuccin flavor, or a
                `rich.terminal_theme.TerminalTheme` object.
            background: override the terminal background color (hex).
            foreground: override the terminal foreground color (hex).
            syntax_theme: override the pygments style used by `code()`.
            font: a locally installed monospace font name, or a sequence of
                names used as fallbacks, e.g. `['JetBrains Mono', 'Consolas']`.
                when given, the svg is rewritten to use it instead of the CDN
                hosted Fira Code, which makes the rasterized png
                deterministic.
            font_size: the font size in px.
            line_height: the line height in px. defaults to `font_size * 1.22`.
                should be >= `font_size`, otherwise glyphs are clipped.
            ligatures: whether to enable font ligatures.
            scale: the device scale factor used by `save_png()`.
            window_title: the caption in the svg window chrome.
            prompt: the default prompt character of `command()`.
        """
        if width < 1:
            raise ValueError('width should be >= 1, got {}'.format(width))
        if font_size < 1:
            raise ValueError(
                'font_size should be >= 1, got {}'.format(font_size)
            )
        if line_height is None:
            line_height = font_size * 1.22
        if line_height < font_size:
            raise ValueError(
                'line_height should be >= font_size ({}), got {}'.format(
                    font_size, line_height
                )
            )

        self.width = width

        self._title = title
        self._command = command
        self._prompt = prompt
        self._font = font
        self._font_size = font_size
        self._line_height = line_height
        self._ligatures = ligatures
        self._scale = scale
        self._window_title = window_title
        self._spec: ThemeSpec = resolve_theme(
            theme,
            background=background,
            foreground=foreground,
            syntax_theme=syntax_theme,
        )
        self._console = Console(
            width=width,
            height=25,
            #   an explicit height keeps `width` effective when rich treats
            #   the environment as a dumb terminal (e.g. TERM=dumb).
            record=True,
            force_terminal=True,
            color_system='truecolor',
            safe_box=False,
            legacy_windows=False,
            file=io.StringIO(),
        )

        self._capturing = False
        self._stream: tp.Optional[_ConsoleStream] = None
        self._old_stdout: tp.Optional[tp.TextIO] = None
        self._old_stderr: tp.Optional[tp.TextIO] = None
        self._old_columns: tp.Optional[str] = None
        self._old_sizes: tp.Optional[
            tp.Tuple[int, tp.Tuple[int, int], tp.Tuple[int, int]]
        ] = None

    # -------------------------------------------------------------------------
    # content

    def title(self, text: str, style: tp.Optional[str] = None) -> None:
        """Print a centered, bold line."""
        self._console.print(
            Text(text, style=style or self._spec.title_style), justify='center'
        )

    def command(
        self,
        text: str,
        prompt: tp.Optional[str] = None,
        style: tp.Optional[str] = None,
    ) -> None:
        """Print a shell command line, e.g. `$ python main.py hello`."""
        prompt = self._prompt if prompt is None else prompt
        parts: tp.List[tp.Tuple[str, str]] = []
        if prompt:
            parts.append((prompt + ' ', self._spec.prompt_style))
        parts.append((text, style or self._spec.foreground or 'default'))
        self._console.print(Text.assemble(*parts))

    def divider(self, char: str = '─', style: tp.Optional[str] = None) -> None:
        """Print a full-width divider line."""
        self._console.print(
            Text(char * self.width, style=style or self._spec.divider_style)
        )

    def print(self, *objects: tp.Any, **kwargs: tp.Any) -> None:
        """Print through the recording console."""
        kwargs.setdefault('highlight', False)
        self._console.print(*objects, **kwargs)

    def code(
        self,
        code: str,
        language: str = 'python',
        *,
        theme: tp.Optional[str] = None,
        line_numbers: bool = False,
        word_wrap: bool = False,
        dedent: bool = True,
    ) -> None:
        """Print a syntax highlighted code block."""
        self._console.print(
            Syntax(
                code,
                language,
                theme=theme or self._spec.syntax,
                background_color=self._spec.background,
                line_numbers=line_numbers,
                word_wrap=word_wrap,
                dedent=dedent,
            )
        )

    # -------------------------------------------------------------------------
    # capture

    @contextmanager
    def capture(self) -> tp.Iterator['Termshot']:
        """Capture everything written to stdout and stderr in the block."""
        self._start_capture()
        try:
            yield self
        finally:
            self._stop_capture()

    def __enter__(self) -> 'Termshot':
        self._start_capture()
        self._print_header()
        return self

    def __exit__(self, *_: tp.Any) -> None:
        self._stop_capture()

    def _print_header(self) -> None:
        if self._title:
            self.title(self._title)
            self.divider()
        if self._command:
            self.command(self._command)

    def _start_capture(self) -> None:
        if self._capturing:
            raise RuntimeError('this termshot is already capturing.')
        self._capturing = True

        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        self._old_columns = os.environ.get('COLUMNS')
        self._old_sizes = (
            _config.console_width,
            (rich_console.width, rich_console.height),
            (legacy_rich_console.width, legacy_rich_console.height),
        )

        stream = _ConsoleStream(self._console, self.width)
        self._stream = stream
        sys.stdout = stream
        sys.stderr = stream
        os.environ['COLUMNS'] = str(self.width)
        _config(console_width=self.width)
        rich_console.size = (self.width, rich_console.height)
        legacy_rich_console.size = (self.width, legacy_rich_console.height)

    def _stop_capture(self) -> None:
        if not self._capturing:
            return
        self._capturing = False

        try:
            if self._stream is not None:
                self._stream.flush_pending()
        finally:
            assert self._old_stdout is not None
            assert self._old_stderr is not None
            assert self._old_sizes is not None
            old_config_width, old_rich_size, old_legacy_size = self._old_sizes
            sys.stdout = self._old_stdout
            sys.stderr = self._old_stderr
            if self._old_columns is None:
                os.environ.pop('COLUMNS', None)
            else:
                os.environ['COLUMNS'] = self._old_columns
            _config(console_width=old_config_width)
            rich_console.size = old_rich_size
            legacy_rich_console.size = old_legacy_size
            self._stream = None

    # -------------------------------------------------------------------------
    # export

    def save_svg(
        self,
        path: tp.Union[str, Path],
        *,
        title: tp.Optional[str] = None,
        theme: tp.Optional[TerminalTheme] = None,
        clear: bool = False,
    ) -> None:
        """
        Save the recording as an svg.

        params:
            title: the caption in the window chrome. defaults to
                `window_title`.
            theme: override the palette used for the export.
            clear: clear the recorded output after saving.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._console.save_svg(
            str(path),
            title=title or self._window_title,
            theme=theme or self._spec.terminal,
            clear=clear,
        )
        apply_style(
            path,
            font=self._font,
            font_size=self._font_size,
            line_height=self._line_height,
            ligatures=self._ligatures,
        )

    def save_png(
        self,
        path: tp.Union[str, Path],
        *,
        scale: tp.Optional[int] = None,
        browser: tp.Optional[str] = None,
        clear: bool = False,
    ) -> None:
        """
        Save the recording as a png.

        The svg is written to a temporary file and rasterized with a headless
        Chrome, Edge, or Chromium.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix='neoprint-termshot-') as tmp:
            svg = Path(tmp) / 'termshot.svg'
            self.save_svg(svg, clear=clear)
            svg_to_png(svg, path, scale=scale or self._scale, browser=browser)

    def save(self, path: tp.Union[str, Path], **kwargs: tp.Any) -> None:
        """Save by suffix: `.svg` or `.png`."""
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix == '.svg':
            self.save_svg(path, **kwargs)
        elif suffix == '.png':
            self.save_png(path, **kwargs)
        else:
            raise ValueError(
                'expected a .svg or .png path, got {!r}'.format(str(path))
            )


class _ConsoleStream:
    """
    Forward stdout writes into a recording console.

    Neoprint (and plain `print`) write ANSI colored text to stdout. We decode
    the escapes into rich text, so the colors survive the round trip. Carriage
    returns are emulated by keeping the last overwrite of a line, which is what
    a progress bar leaves on screen.
    """

    encoding = 'utf-8'

    def __init__(self, console: Console, width: int) -> None:
        self._console = console
        self.columns = width
        self._buffer = ''

    def write(self, text: str) -> int:
        self._buffer += text
        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            self._emit(line)
        return len(text)

    def flush(self) -> None:
        #   a flush does not advance a terminal line, so there is nothing to
        #   emit here. a partial line is emitted at the end of the capture, or
        #   when a newline arrives.
        pass

    def flush_pending(self) -> None:
        if self._buffer:
            line, self._buffer = self._buffer, ''
            self._emit(line)

    def isatty(self) -> bool:
        return False

    def _emit(self, line: str) -> None:
        line = line.rstrip('\r').split('\r')[-1]
        line = _ERASE_LINE.sub('', line)
        line = _OTHER_CSI.sub('', line)
        self._console.print(Text.from_ansi(line), highlight=False)


def termshot(**kwargs: tp.Any) -> Termshot:
    """Create a `Termshot`. See `Termshot` for the parameters."""
    return Termshot(**kwargs)
