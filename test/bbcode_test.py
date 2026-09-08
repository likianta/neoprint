import neoprint as np
from argsense import cli
from neoprint.render import translate


@cli
def bbcode_to_anscii() -> None:
    # classic
    result = tuple(translate('[red]hello[/] [green]world[/]'))
    assert result == (
        ('hello', 'red', ''),
        (' ', 'default', ''),
        ('world', 'green', ''),
    )

    # style
    result = tuple(translate('[red bold]hello[/]'))
    assert result == (('hello', 'red', 'bold'),)

    # nested
    result = tuple(
        translate('[red bold]aaa [green]bbb[/] [italic]ccc[/] ddd[/]')
    )
    assert result == (
        ('aaa ', 'red', 'bold'),
        ('bbb', 'green', 'bold'),
        (' ', 'red', 'bold'),
        ('ccc', 'red', 'italic'),
        (' ddd', 'red', 'bold'),
    )


@cli
def nested_bbcode() -> None:
    np.show('[green]AAA [dim]BBB[/] [default dim]CCC[/] DDD[/]', ':r')
    np.show('[red dim]EEE [default nodim]FFF[/] GGG[/]', ':r')
    np.show('HHH [dim]III[/] [green]JJJ[/]', ':rv8')


if __name__ == '__main__':
    cli.run()
