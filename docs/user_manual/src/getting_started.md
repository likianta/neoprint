# Installation and Hello World

## Requirements

- Python 3.9 or newer
- A modern terminal. Windows Terminal, iTerm2, GNOME Terminal, and the
  integrated terminals of VS Code and PyCharm all work. If colors look wrong on
  an old Windows console, see [Configuration](./reference/configuration.md).

## Install

```sh
pip install neoprint
```

The only runtime dependency is `rich`.

## Hello world

```python
import neoprint as np

np.show('hello world')
```

```text
main.py:3   | hello world
```

The message is made of two parts:

- a **head** — `main.py:3` — showing where the call happened,
- a **body** — `hello world` — the text you passed.

A thin `|` separator sits between them. Both parts are colored: the file name
is blue, the line number green, the separator dim.

## Use it as `print`

`neoprint.print` is a plain alias of `neoprint.show`, so you can keep the name
you are used to:

```python
from neoprint import print

print('hello world')
```

If you want to swap it in for an entire script without touching every call,
simply shadow the built-in:

```python
from neoprint import print

print('this is neoprint now', 1, 2, 3)
```

Note that the built-in `print` accepts keyword arguments such as `file=` and
`end=`. Neoprint's print does not; for those cases use the mark `:s2` (see
[Printing Basics](./basic_usage.md)) or the real `builtins.print`.

## Enable it for a whole package

Editing imports in every module is noisy. Call `setup()` once in your
package's `__init__.py`:

```python
# some_package/__init__.py
import neoprint
neoprint.setup()

# regular exports
from .foo import bar
```

From then on, every built-in `print(...)` call **inside `some_package`** is
routed through neoprint automatically. Calls in other packages, and in the
standard library, keep using the built-in `print` — `setup()` patches the
built-in only for the package that called it.

To undo the patch:

```python
import neoprint
neoprint.unload()
```

## Try the examples

The repository ships runnable examples:

```sh
python examples/hello_world.py
python examples/all_markup_usage.py
python examples/progress.py
```

Next: [Printing Basics](./basic_usage.md).
