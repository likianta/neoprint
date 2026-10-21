"""
Generate the user manual illustrations with neoprint.termshot.

The png files are saved in `docs/user_manual/src/images`, and the svg files
they are rasterized from are kept in `docs/user_manual/src/images/svg`.

Every scene is executed from a script in
`docs/user_manual/src/images/.scenes`, so the source location printed by
neoprint shows a natural file name (e.g. `hello_world.py:4`) instead of this
generator. Those scripts are kept for reference.

Usage:
    python docs/user_manual/generate_images.py
"""

import io
from contextlib import redirect_stdout
from pathlib import Path
from random import seed
from textwrap import dedent

from argsense import cli
import neoprint as np

MDBOOK_ROOT = Path(__file__).resolve().parent.parent
IMAGES = MDBOOK_ROOT / 'docs' / 'images'
SVGS = IMAGES / 'svg'
SCENES = MDBOOK_ROOT / 'scripts' / 'scenes'

FONT = ('Fira Code Medium', 'Consolas', 'monospace')
FONT_SIZE = 15
LINE_HEIGHT = FONT_SIZE * 1.3
LIGATURES = False
THEME = 'catppuccin-mocha'
SCALE = 2


def main(unit: str = 'all') -> None:
    seed(0)  # keep the random index colors stable across runs.
    IMAGES.mkdir(parents=True, exist_ok=True)
    SVGS.mkdir(exist_ok=True)
    SCENES.mkdir(exist_ok=True)
    if unit == 'all':
        _render_index_hero()
        _render_hello_world()
        _render_basic_arguments()
        _render_verbosity_levels()
        _render_varnames()
        _render_expanded_tree()
        _render_expanded_layouts()
        _render_rich_text_styles()
        _render_index_counter()
        _render_index_scopes()
        _render_timing()
        _render_dividers()
        _render_exception_panel()
        _render_parent_layers()
        _render_progress_bar()
        _render_progress_indicators()
    else:
        globals()['_render_{}'.format(unit)]()


def _render_index_hero() -> None:
    render(
        'index-hero',
        'Neoprint',
        'python main.py',
        86,
        'main.py',
        """
        import neoprint as np

        name = 'Alice'
        age = 30
        np.show(name, age, ':n')

        np.show(
            '[bold cyan]colors[/], [green]varnames[/], '
            '[yellow]progress bars[/]',
            ':r',
        )
        np.show(':v4', 'SUCCESS: pretty output, one dependency')
        np.show(':d2', 'ready')
        """,
    )


def _render_hello_world() -> None:
    render(
        'hello-world',
        'Hello World',
        'python hello_world.py',
        70,
        'hello_world.py',
        """
        import neoprint as np

        np.show('hello world')
        """,
    )


def _render_basic_arguments() -> None:
    render(
        'basic-arguments',
        'Semicolon-Joined Arguments',
        'python basic_arguments.py',
        86,
        'basic_arguments.py',
        """
        import neoprint as np

        np.show('Multiple', 'arguments', 'are', 'semicolon-separated')
        np.show(123, 456, 'mixed types', True, False, None)
        """,
    )


def _render_verbosity_levels() -> None:
    render(
        'verbosity-levels',
        'Verbosity Levels',
        'python verbosity.py',
        84,
        'verbosity.py',
        """
        import neoprint as np

        np.show(':v0', 'v0 debug')
        np.show(':v1', 'v1 negative info')
        np.show(':v2', 'v2 positive info')
        np.show(':v3', 'v3 weak success')
        np.show(':v4', 'v4 success')
        np.show(':v5', 'v5 weak warning')
        np.show(':v6', 'v6 warning')
        np.show(':v7', 'v7 weak error')
        np.show(':v8', 'v8 error')
        """,
    )


def _render_varnames() -> None:
    render(
        'varnames',
        'Variable Names',
        'python varnames.py',
        78,
        'varnames.py',
        """
        import neoprint as np

        name = 'Alice'
        age = 30
        city = 'New York'
        np.show(name, age, city, ':n')

        names = ['Alice', 'Bob']
        np.show(len(names), ':n')

        class Box:
            def __init__(self):
                self.value = 42

        box = Box()
        np.show(box.value, ':n')
        """,
    )


def _render_expanded_tree() -> None:
    render(
        'expanded-tree',
        'Expanded Tree',
        'python expanded_format.py',
        76,
        'expanded_format.py',
        """
        import neoprint as np

        data = {
            'users': [
                {'name': 'Alice', 'tags': ['dev', 'ops']},
                {'name': 'Bob', 'tags': ['design']},
            ]
        }
        np.show(data, ':l')
        """,
    )


def _render_expanded_layouts() -> None:
    render(
        'expanded-layouts',
        'Tailored Layouts',
        'python layouts.py',
        78,
        'layouts.py',
        """
        import neoprint as np

        np.show(':l2', [('id', 'name'), ('1', 'Alice'), ('2', 'Bob')])
        np.show(':l2', {'name': 'neoprint', 'version': '1.0.0'})
        np.show(':l2', 'status: draft -> published')
        """,
    )


def _render_rich_text_styles() -> None:
    render(
        'rich-text-styles',
        'Rich Text',
        'python rich_text.py',
        80,
        'rich_text.py',
        """
        import neoprint as np

        np.show(':r1', '[red]red[/] [green bold]green bold[/] [dim]dim[/]')
        np.show(':r1', '[red bold]both[/] [red]red only[/]')
        np.show(':r1', '[red bold]outer [green]green keeps bold[/][/]')
        """,
    )


def _render_index_counter() -> None:
    render(
        'index-counter',
        'Index Counters',
        'python index_counter.py',
        70,
        'index_counter.py',
        """
        import neoprint as np

        np.show(':i2', 'first')
        np.show(':i2', 'second')
        np.show(':i2', 'third')
        """,
    )


def _render_index_scopes() -> None:
    render(
        'index-scopes',
        'Custom Scopes',
        'python scopes.py',
        74,
        'scopes.py',
        """
        import neoprint as np

        with np.scope(name='download'):
            np.show(':i2', 'file A')
            np.show(':i2', 'file B')

        with np.scope():
            np.show(':i2', 'anonymous 1')
        """,
    )


def _render_timing() -> None:
    render(
        'timing',
        'Timing',
        'python timing.py',
        82,
        'timing.py',
        """
        import neoprint as np
        from time import sleep

        np.show(':t', 'starting')
        sleep(0.2)
        np.show(':t', 'loaded config')
        sleep(0.5)
        np.show(':t', 'connected')
        """,
        reset_timer=True,
    )


def _render_short_timing() -> None:
    render(
        'short-timing',
        'Timing In Short Form',
        'python short_timing.py',
        82,
        'short_timing.py',
        """
        import neoprint as np
        from time import sleep

        np.config(show_source=False)

        np.show(':dv', 'duration in default form')

        np.show(':t', 'ONE')
        sleep(0.3)
        np.show(':t', 'TWO')
        sleep(0.7)
        np.show(':t', 'THREE')
        sleep(1.2)
        np.show(':t', 'FOUR')
        sleep(5)
        np.show(':t', 'FIVE')

        np.show(':dv', 'duration in short form')

        np.show(':ts', 'ONE')
        sleep(0.3)
        np.show(':ts', 'TWO')
        sleep(0.7)
        np.show(':ts', 'THREE')
        sleep(1.2)
        np.show(':ts', 'FOUR')
        sleep(5)
        np.show(':ts', 'FIVE')

        """,
        reset_timer=True,
    )


def _render_dividers() -> None:
    render(
        'dividers',
        'Dividers',
        'python dividers.py',
        86,
        'dividers.py',
        """
        import neoprint as np

        np.show(':d')  # thin gray line
        np.show(':d1', 'thin')
        np.show('some line')
        np.show(':d2', 'thick')
        np.show(':d2v7t', 'End')
        """,
        reset_timer=True,
    )


def _render_exception_panel() -> None:
    render(
        'exception-panel',
        'Traceback Panel',
        'python exception_panel.py',
        94,
        'exception_panel.py',
        """
        import neoprint as np

        try:
            result = 1 / 0
        except ZeroDivisionError as e:
            np.show(e, ':e2')
        """,
    )


def _render_parent_layers() -> None:
    render(
        'parent-layers',
        'Source Layers',
        'python parent_layer.py',
        76,
        'parent_layer.py',
        """
        import neoprint as np

        np.config(show_funcname=True)

        def aaa():
            def bbb():
                def ccc():
                    np.show('👈 in "ccc" function', ':p0')
                    np.show('👈 in "bbb" function', ':p1')
                    np.show('👈 in "aaa" function', ':p2')
                    np.show('👈 in "<module>" scope', ':p3')

                ccc()
            bbb()
        aaa()
        """,
    )


def _render_progress_bar() -> None:
    render(
        'progress-bar',
        'Progress Bar',
        'python progress.py',
        86,
        'progress.py',
        """
        import neoprint as np

        names = ['Alice', 'Bob', 'Carol']

        with np.Progress(total=len(names)) as prog:
            for name in names:
                prog.update(name)
        """,
    )


def _render_progress_indicators() -> None:
    render(
        'progress-indicators',
        'Progress Indicators',
        'python progress_indicators.py',
        80,
        'progress_indicators.py',
        """
        import neoprint as np

        with np.Progress(
            total=100, indicator_style='decimal', color='green'
        ) as p:
            for i in range(42):
                p.update()
        """,
    )


def render(
    name: str,
    title: str,
    command: str,
    width: int,
    filename: str,
    code: str,
    *,
    reset_timer: bool = False,
) -> None:
    source = dedent(code).strip('\n')
    shot = np.termshot(
        title=title,
        command=command,
        width=width,
        theme=THEME,
        font=FONT,
        font_size=FONT_SIZE,
        line_height=LINE_HEIGHT,
        ligatures=LIGATURES,
    )

    if reset_timer:
        #   `:t0` prints nothing, but it makes the first `:t` show a
        #   meaningful delta instead of the time since this script started.
        with redirect_stdout(io.StringIO()):
            np.show(':t0')

    scene = SCENES / filename
    scene.write_text(source, encoding='utf-8')
    relative = scene.relative_to(MDBOOK_ROOT.parent.parent).as_posix()
    with shot:
        exec(
            compile(source, relative, 'exec'),
            {'__name__': '__main__', '__file__': str(scene)},
        )

    svg = SVGS / '{}.svg'.format(name)
    png = IMAGES / '{}.png'.format(name)
    shot.save_svg(svg)
    shot.save_png(png, scale=SCALE)
    print('wrote', png.relative_to(MDBOOK_ROOT.parent.parent))


if __name__ == '__main__':
    cli.run(main)
