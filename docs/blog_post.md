# Whether Do We Need Another Print — Meet Neoprint

Modern terminals are capable of far more than plain monochrome text: true
color, emphasis, layout, and live animation. We spend our whole day staring at
console output, so why should it look like it's still 1985?

Color alone makes a surprising difference. Compare IPython with and without
syntax highlighting:

![](images/261020-160929.png)

Layout matters just as much. Ideally, a single trivial call should already tell
you *where* the output came from, *what* the variable was called, and *how* the
object is structured:

![](images/261020-161807.png)

![](images/261020-162057.gif)

That is exactly what **[Neoprint](https://github.com/likianta/neoprint)** is
built for. It is a drop-in replacement for `print` (almost the same API) that
emits colorful, neatly re-formatted output in any modern terminal.

## Why another print library?

There are plenty of great logging and pretty-printing libraries out there, but
they usually ask you to change the way you work: switch to a logger, register
a formatter, adopt a whole framework. Neoprint takes the opposite approach.
Keep writing `print(...)` like you always have, and get the extras for free:

- **Colors and styles** — from BBCode-ish inline markup to 256-color and
  true-color output.
- **Variable names for free** — `print(x, y, ':n')` shows `x = ...; y = ...`
  without you repeating yourself.
- **Readable object dumps** — with `:l`, nested lists, dicts, and dataclasses
  are laid out so you can actually read them.
- **Where did this print come from?** — file and line are shown automatically.
- **Progress bars and spinners** — built in, no extra dependency.
- **Pretty tracebacks** — bring the Rich traceback panel to any exception with a
  single flag.

All of this with exactly one dependency: `rich`.

## Installation

```sh
pip install neoprint
```

Neoprint supports Python 3.9 and above, and pulls in nothing but `rich`.

## Quick start

### Use it in a single script

```python
from neoprint import print

print('hello world')
```

That's it — same name, same call signature. You can drop it in front of any
existing script and immediately get colored, annotated output.

### Make it global across a package

If you want *every* module under a package to use the enhanced `print` without
editing each import, call `setup()` once in the package's `__init__.py`:

```python
# in your some_package/__init__.py, write this:
import neoprint
neoprint.setup()

# then the regular exports
from .foo import bar
...
```

From that point on, every `print` statement inside `some_package/**` is enhanced
automatically. No monkey-patching in user code, no per-file boilerplate.

## A taste of what you get

Because it is just `print`, you can adopt Neoprint incrementally. Extra
features are unlocked by a tiny "mark" string you append to the call (or pass
as the first argument) — nothing else changes:

```python
from neoprint import print

name = 'Alice'
age = 30
print(name, age, ':n')   # shows: name = "Alice"; age = 30
```

Nested structures can be re-flowed into a readable tree instead of one endless
line, just by adding `:l`:

```python
data = {'users': [{'name': 'Alice', 'tags': ['dev', 'ops']},
                  {'name': 'Bob', 'tags': ['design']}]}
print(data, ':l')
```

And when something goes wrong, you get a proper traceback panel rather than a
bare `Traceback (most recent call last):` dump:

```python
try:
    1 / 0
except ZeroDivisionError as e:
    print(e, ':e')
```

If you want more, there are opt-in marks for indexing (`:i`), timing (`:t`),
verbosity levels (`:v`), inline markup, progress bars, and more — but you never
have to learn them to get started. Plain `print` already works better.

## Learn more

Neoprint is open source. You can find it on GitHub:
<https://github.com/likianta/neoprint>.

The full documentation lives here: <https://likianta.github.io/neoprint/>

If it saves you a little time in your terminal, a star on GitHub goes a long
way — and issues or PRs are always welcome.
