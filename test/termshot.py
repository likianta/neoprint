"""
Validate the termshot feature.

It records neoprint output (and plain prints), draws a centered title, a
command line, a divider and a syntax highlighted code block, then exports
both an svg and a png.

Usage:
    python test/termshot.py
"""

from pathlib import Path

import neoprint as np

HERE = Path(__file__).resolve().parent
OUT = HERE / '_termshot_output'


def main() -> None:
    OUT.mkdir(exist_ok=True)
    width_before = np.config.console_width

    shot = np.termshot(
        title='Neoprint Termshot',
        command='python main.py hello',
        width=100,
        theme='catppuccin-mocha',
    )
    with shot:
        name = 'Alice'
        age = 30
        np.show(name, age, ':n')
        np.show('hello world', ':v4')
        print('plain print() is captured too.')
        shot.code("import neoprint as np\n\nnp.show('hello', ':v4')", 'python')

    svg = OUT / 'demo.svg'
    png = OUT / 'demo.png'
    shot.save_svg(svg)
    shot.save_png(png, scale=2)
    print('wrote', svg)
    print('wrote', png)

    # a custom background, a font fallback and custom metrics.
    custom = np.termshot(
        title='Custom colors',
        width=72,
        background='#101820',
        foreground='#f2f2f2',
        syntax_theme='monokai',
        font=['Cascadia Code', 'Consolas'],
        font_size=16,
        line_height=22,
        ligatures=False,
    )
    with custom:
        print('background and foreground are overridden.')
        custom.divider('-')
        custom.code('print("hello")', 'python')
    custom_svg = OUT / 'custom.svg'
    custom_png = OUT / 'custom.png'
    custom.save_svg(custom_svg)
    custom.save_png(custom_png, scale=2)
    print('wrote', custom_svg)
    print('wrote', custom_png)

    text = custom_svg.read_text(encoding='utf-8')
    assert "font-family: 'Cascadia Code', 'Consolas', monospace;" in text
    assert 'font-size: 16px;' in text
    assert 'line-height: 22px;' in text
    assert 'font-variant-ligatures: none;' in text

    assert np.config.console_width == width_before
    assert svg.stat().st_size > 0
    assert png.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
    assert custom_png.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
    print('ok')


if __name__ == '__main__':
    main()
