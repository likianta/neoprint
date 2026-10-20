import typing as tp
from dataclasses import dataclass
from dataclasses import replace

from rich.terminal_theme import SVG_EXPORT_THEME
from rich.terminal_theme import TerminalTheme

_CATPPUCCIN_FLAVORS = ('latte', 'frappe', 'macchiato', 'mocha')


@dataclass(frozen=True)
class ThemeSpec:
    """
    The resolved colors used by a termshot.

    Attributes:
        terminal: The palette that rich uses to export the svg.
        syntax: The pygments style used by `Termshot.code()`.
        background: The background color of code blocks, in hex.
        foreground: The default body color, in hex.
        title_style: The rich style of a title.
        prompt_style: The rich style of a command prompt.
        divider_style: The rich style of a divider.
    """

    terminal: TerminalTheme
    syntax: str
    background: tp.Optional[str] = None
    foreground: tp.Optional[str] = None
    title_style: str = 'bold'
    prompt_style: str = 'bold green'
    divider_style: str = 'dim'


def resolve_theme(
    theme: tp.Union[str, TerminalTheme, None] = None,
    *,
    background: tp.Optional[str] = None,
    foreground: tp.Optional[str] = None,
    syntax_theme: tp.Optional[str] = None,
) -> ThemeSpec:
    """
    Turn the user facing `theme` names into a `ThemeSpec`.

    params:
        theme:
            - None or 'default': rich's default svg palette.
            - 'catppuccin' or 'catppuccin-<flavor>': a catppuccin flavor,
              where flavor is one of latte, frappe, macchiato, mocha.
              The short flavor name ('mocha') is also accepted.
            - a `TerminalTheme` object: use it as-is.
        background: override the terminal background color (hex).
        foreground: override the terminal foreground color (hex).
        syntax_theme: override the pygments style used by code blocks.
    """
    spec = _resolve_base_theme(theme)

    if background is not None or foreground is not None:
        ansi_colors = _get_ansi_colors(spec.terminal)
        spec = replace(
            spec,
            terminal=TerminalTheme(
                background=(
                    _hex_to_rgb(background)
                    if background is not None
                    else _get_background(spec.terminal)
                ),
                foreground=(
                    _hex_to_rgb(foreground)
                    if foreground is not None
                    else _get_foreground(spec.terminal)
                ),
                normal=ansi_colors[:8],
                bright=ansi_colors[8:],
            ),
            background=background or spec.background,
            foreground=foreground or spec.foreground,
        )

    if syntax_theme:
        spec = replace(spec, syntax=syntax_theme)

    return spec


def _resolve_base_theme(theme: tp.Union[str, TerminalTheme, None]) -> ThemeSpec:
    if theme is None:
        return _default_theme()

    if isinstance(theme, TerminalTheme):
        return replace(_default_theme(), terminal=theme)

    if not isinstance(theme, str):
        raise TypeError(
            'theme should be a string or a TerminalTheme, got {!r}'.format(
                type(theme)
            )
        )

    name = theme.strip().lower().replace('_', '-')
    if name in ('', 'default'):
        return _default_theme()

    if name == 'catppuccin':
        name = 'catppuccin-mocha'

    if name.startswith('catppuccin-'):
        flavor = name[len('catppuccin-') :]
    elif name in _CATPPUCCIN_FLAVORS:
        flavor = name
    else:
        raise ValueError(
            "unknown theme {!r}. expected 'default', a catppuccin flavor "
            "('latte', 'frappe', 'macchiato', 'mocha'), or a TerminalTheme "
            'object.'.format(theme)
        )

    if flavor not in _CATPPUCCIN_FLAVORS:
        raise ValueError(
            'unknown catppuccin flavor {!r}. expected one of {}.'.format(
                flavor, ', '.join(_CATPPUCCIN_FLAVORS)
            )
        )

    return _catppuccin_theme(flavor)


def _default_theme() -> ThemeSpec:
    return ThemeSpec(
        terminal=SVG_EXPORT_THEME,
        syntax='monokai',
        background=None,
        foreground=None,
        title_style='bold bright_cyan',
        prompt_style='bold green',
        divider_style='dim',
    )


def _catppuccin_theme(flavor: str) -> ThemeSpec:
    try:
        import catppuccin
    except ImportError as exc:
        raise ImportError(
            'catppuccin is required for theme {!r}. install it with: '
            "pip install 'neoprint[termshot]'".format('catppuccin-' + flavor)
        ) from exc

    colors = getattr(catppuccin.PALETTE, flavor).colors

    def rgb(name: str) -> tp.Tuple[int, int, int]:
        color = getattr(colors, name).rgb
        return color.r, color.g, color.b

    normal = [
        rgb('surface1'),
        rgb('red'),
        rgb('green'),
        rgb('yellow'),
        rgb('blue'),
        rgb('pink'),
        rgb('teal'),
        rgb('subtext1'),
    ]
    bright = [
        rgb('surface2'),
        rgb('red'),
        rgb('green'),
        rgb('yellow'),
        rgb('blue'),
        rgb('pink'),
        rgb('teal'),
        rgb('subtext0'),
    ]

    return ThemeSpec(
        terminal=TerminalTheme(
            background=rgb('base'),
            foreground=rgb('text'),
            normal=normal,
            bright=bright,
        ),
        syntax='catppuccin-{}'.format(flavor),
        background=colors.base.hex,
        foreground=colors.text.hex,
        title_style='bold {}'.format(colors.mauve.hex),
        prompt_style='bold {}'.format(colors.green.hex),
        divider_style=colors.overlay0.hex,
    )


def _hex_to_rgb(value: str) -> tp.Tuple[int, int, int]:
    text = value.strip().lstrip('#')
    if len(text) != 6:
        raise ValueError(
            'expected a hex color like #1e1e2e, got {!r}'.format(value)
        )
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def _get_background(theme: TerminalTheme) -> tp.Tuple[int, int, int]:
    color = tp.cast(tp.Any, theme).background_color
    return color.red, color.green, color.blue


def _get_foreground(theme: TerminalTheme) -> tp.Tuple[int, int, int]:
    color = tp.cast(tp.Any, theme).foreground_color
    return color.red, color.green, color.blue


def _get_ansi_colors(theme: TerminalTheme) -> tp.List[tp.Tuple[int, int, int]]:
    palette = tp.cast(tp.Any, theme).ansi_colors
    return [tuple(color) for color in palette]
