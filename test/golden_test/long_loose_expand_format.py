import neoprint as np
import os
from argsense import cli
from objprint import op
from faker import Faker


@cli
def main():
    filenames = os.listdir('neoprint')
    filenames_rev = filenames[::-1]
    np.show(':l', filenames)
    np.show(':nl', filenames, filenames_rev)
    np.show(':nlv6', filenames)
    # np.show(':l2', 'installation done: v0.1.0 -> v0.2.0')
    # np.show(
    #     ':l2',
    #     (
    #         ('index', 'name', 'age', 'city'),
    #         ('1', 'AAA', '20', 'New York'),
    #         ('2', 'BBB', '24', 'Los Angeles'),
    #         ('3', 'CCC', '28', 'Chicago'),
    #     ),
    #     {
    #         'name': 'neoprint',
    #         'version': '0.1.0',
    #         'code': 0xFFFF,
    #         'author': 'Likianta',
    #     },
    #     'AAA -> BBB',
    #     'CCC: DDD -> EEE',
    # )

    # ---

    # output0 = np.util.strip_ansi(np.debugger.output[0])
    # lines0 = output0.splitlines()
    # assert len(lines0) > 1
    # assert lines0[0] == 'long_loose_expand_format.py:8   | '
    # assert lines0[1] == '  ['
    # assert lines0[2] == '    "capture.py",'
    # assert lines0[3] == '    "config.py",'
    # ...
    # assert lines0[-1] == '  ]'

    # output1 = np.util.strip_ansi(np.debugger.output[1])
    # lines1 = output1.splitlines()
    # assert lines1[0] == 'long_loose_expand_format.py:9   | '
    # assert lines1[1] == '  filenames = ['
    # flag = 'INIT'
    # for line in lines1[2:]:
    #     if flag == 'INIT':
    #         if line.lstrip().startswith(']'):
    #             assert line == '  ],'
    #             flag = 'CHECK_REV_START'
    #         continue
    #     if flag == 'CHECK_REV_START':
    #         assert line == '  filenames_rev = ['
    #         break

    # output2 = np.util.ansi_to_bbcode(np.debugger.output[2])
    # lines2 = output2.splitlines()
    # assert lines2[0] == (
    #     '[bold blue]long_loose_expand_format.py[/]'
    #     '[dim blue]:[/]'
    #     '[dim blue]10 [/]'
    #     ' [bright_black]|[/] '
    # )
    # assert lines2[1] == '  [yellow]filenames = \\[[/]'
    # assert lines2[2] == '    [yellow]"capture.py",[/]'
    # assert lines2[-1] == '  [yellow]][/]'

    # output3 = np.util.ansi_to_bbcode(np.debugger.output[3])
    # assert output3 == (
    #     '[bold blue]long_loose_expand_format.py[/]'
    #     '[dim blue]:[/]'
    #     '[dim blue]11 [/]'
    #     ' [bright_black]|[/] '
    #     'installation done: [red]v0.1.0[/] -> [green]v0.2.0[/]'
    #     '\n'
    # ), output3

    # output4 = np.util.strip_ansi(np.debugger.output[4])
    # assert (
    #     """  | KEY     | VALUE    |
    # | ------- | -------- |
    # | name    | neoprint |
    # | version | 0.1.0    |
    # | code    | 65535    |
    # | author  | Likianta |"""
    # ) in output4, output4


@cli
def debug_objstr():
    fk = Faker()

    class Player:
        name = 'Alice'
        age = 20
        city = 'New York'

    op(Player)
    op(Player())
    op(
        {
            'name': fk.name(),
            'phone': fk.phone_number(),
            'city': fk.city(),
            'description': fk.sentence(),
        }
    )
    op(
        [
            ('index', 'name', 'age', 'city'),
            ('1', 'AAA', '20', 'New York'),
            ('2', 'BBB', '24', 'Los Angeles'),
            ('3', 'CCC', '28', 'Chicago'),
        ]
    )


if __name__ == '__main__':
    cli.run()
