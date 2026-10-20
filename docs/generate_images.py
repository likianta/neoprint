"""
Generate the README illustrations with neoprint.termshot.

The png files are saved in `docs/images`, and the svg files they are
rasterized from are kept in `docs/images/svg`.

Every scene is executed from a script in `docs/images/.scenes`, so the
source location printed by neoprint shows a natural file name (e.g.
`hello_world.py:4`) instead of this generator. Those scripts are kept for
reference.

Usage:
    python docs/generate_images.py
"""

import io
from contextlib import redirect_stdout
from pathlib import Path
from random import seed
from textwrap import dedent

import neoprint as np

HERE = Path(__file__).resolve().parent
IMAGES = HERE / 'images'
SVGS = IMAGES / 'svg'
SCENES = IMAGES / '.scenes'

FONT = ('Fira Code Medium', 'Consolas', 'monospace')
FONT_SIZE = 15
LINE_HEIGHT = FONT_SIZE * 1.3
LIGATURES = False
THEME = 'catppuccin-mocha'
SCALE = 2


def main() -> None:
    seed(0)  # keep the random index colors stable across runs.
    IMAGES.mkdir(exist_ok=True)
    SVGS.mkdir(exist_ok=True)
    SCENES.mkdir(exist_ok=True)
    _render_all()


def _render_all() -> None:
    render(
        'neoprint-overview',
        'Neoprint',
        'python main.py',
        88,
        'main.py',
        """
        import neoprint as np

        np.show('[bold cyan]Neoprint[/] - expressive console output', ':r')
        np.show(':d')

        name = 'Alice'
        age = 30
        city = 'New York'
        np.show(name, age, city, ':n')

        np.show(':v2', 'INFO message - cyan')
        np.show(':v4', 'SUCCESS message - bright green')
        np.show(':v6', 'WARNING message - bright yellow')
        np.show(':v8', 'ERROR message - bright red')

        np.show(':i2', 'indexed item')
        np.show(':d')
        np.show('[green]everything in one place[/]', ':r')
        """,
    )

    render(
        'hello-world',
        'Hello World',
        'python hello_world.py',
        76,
        'hello_world.py',
        """
        import neoprint as np

        np.show('Hello, World!')
        np.show('Multiple', 'arguments', 'are', 'semicolon-separated')
        np.show(123, 456, 'mixed types', True, False, None)
        """,
    )

    render(
        'variable-names',
        'Variable Names',
        'python variable_names.py',
        70,
        'variable_names.py',
        """
        import neoprint as np

        name = 'Alice'
        age = 30
        city = 'New York'
        np.show(name, age, city, ':n')
        """,
    )

    render(
        'verbosity-levels',
        'Highlighting and Verbosity Levels',
        'python verbosity.py',
        84,
        'verbosity.py',
        """
        import neoprint as np

        np.show('[red]error[/] [yellow]warning[/] [green]success[/]', ':r')
        np.show(':v1', 'DEBUG message - dim gray')
        np.show(':v2', 'INFO message - cyan')
        np.show(':v4', 'SUCCESS message - bright green')
        np.show(':v6', 'WARNING message - bright yellow')
        np.show(':v8', 'ERROR message - bright red')
        np.debug('This is a debug message')
        np.info('This is an info message')
        np.success('This is a success message')
        np.warning('This is a warning message')
        np.error('This is an error message')
        """,
    )

    render(
        'index-counter',
        'Index Counter',
        'python index_counter.py',
        70,
        'index_counter.py',
        """
        import neoprint as np

        np.show(':i2', 'first item')
        np.show(':i2', 'second item')
        np.show(':i2', 'third item')
        np.show(':i0', 'counter reset')
        np.show(':i2', 'counting starts over')
        """,
    )

    render(
        'timing',
        'Timing',
        'python timing.py',
        76,
        'timing.py',
        """
        import neoprint as np
        from time import sleep

        np.show(':t', 'starting...')
        sleep(1)
        np.show(':t', 'after 1 second')
        sleep(2)
        np.show(':t', 'after 3 seconds total')
        """,
        reset_timer=True,
    )

    render(
        'progress-bar',
        'Progress Bar',
        'python progress.py',
        90,
        'progress.py',
        """
        import neoprint as np

        with np.Progress(total=100) as prog:
            for i in range(68):
                prog.update('Processing item {}'.format(i + 1))
        """,
    )

    render(
        'exception-panel',
        'Exception Formatting',
        'python exception_panel.py',
        94,
        'exception_panel.py',
        """
        import neoprint as np

        try:
            result = 1 / 0
        except ZeroDivisionError:
            np.show(':e')
        """,
    )

    render(
        'custom-scopes',
        'Custom Scopes',
        'python custom_scopes.py',
        76,
        'custom_scopes.py',
        """
        import neoprint as np

        with np.scope():
            np.show(':i2', 'anonymous scope - item 1')
            np.show(':i2', 'anonymous scope - item 2')

        with np.scope(name='MyScope'):
            np.show(':i2', 'MyScope - item 1')
            np.show(':i2', 'MyScope - item 2')
        """,
    )

    render(
        'feature-gallery',
        'Feature Gallery',
        'python gallery.py',
        84,
        'gallery.py',
        """
        import neoprint as np

        np.show(':d', 'colors')
        np.show(
            '[red]red[/] [green]green[/] [yellow]yellow[/] '
            '[blue]blue[/] [magenta]magenta[/] [cyan]cyan[/]',
            ':r',
        )
        np.show(':d', 'styles')
        np.show(
            '[bold]bold[/] [dim]dim[/] [italic]italic[/] '
            '[underline]underline[/]',
            ':r',
        )
        np.show(':d', 'table')
        np.show(':l2', {'Key': 'Value', 'name': 'Alice', 'age': 30})
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
    relative = scene.relative_to(HERE.parent).as_posix()
    with shot:
        exec(
            compile(source, relative, 'exec'),
            {'__name__': '__main__', '__file__': str(scene)},
        )

    svg = SVGS / '{}.svg'.format(name)
    png = IMAGES / '{}.png'.format(name)
    shot.save_svg(svg)
    shot.save_png(png, scale=SCALE)
    print('wrote', png.relative_to(HERE.parent))


if __name__ == '__main__':
    main()
