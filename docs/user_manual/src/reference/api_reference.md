# API Reference

Everything below is available from the package root:

```python
import neoprint as np
```

## Printing

| Name | Signature | Equivalent |
| :--- | :-------- | :--------- |
| `np.show` | `show(*args, markup=None)` | the main entry point |
| `np.print` | `print(*args, markup=None)` | alias of `np.show` |
| `np.debug` | `debug(*args, markup=None)` | `show(..., ':v1')` |
| `np.info` | `info(*args, markup=None)` | `show(..., ':v2')` |
| `np.success` | `success(*args, markup=None)` | `show(..., ':v4')` |
| `np.warning` | `warning(*args, markup=None)` | `show(..., ':v6')` |
| `np.error` | `error(*args, markup=None)` | `show(..., ':v8')` |
| `np.divider` | `divider(*args, markup=None)` | `show(..., ':d1')` |
| `np.exception` | `exception(*args, markup=None)` | `show(..., ':e2')` |
| `np.expand` | `expand(*args, markup=None)` | `show(..., ':l1')` |
| `np.expand2` | `expand2(*args, markup=None)` | `show(..., ':l2')` |
| `np.index` | `index(*args, markup=None)` | `show(..., ':i2')` |

All printing functions return `None`. A markup passed as the first or last
positional argument is merged with the shorthand's own markup, so
`np.warning(x, ':n')` is the same as `np.show(x, ':v6n')`.

`np.vshow` exists as the `:n1` shorthand, but variable-name resolution keys on
the called function name, and `vshow` is not recognizable to the analyzer.
Use `np.show(x, ':n1')` instead.

### markdown

```python
markdown(*args: str) -> None
```

Accept one argument (the Markdown text) or two arguments (the text and a
markup, in either order):

```python
np.markdown('# Title\n\nSome **bold** text.')
np.markdown(':n', '**bold**')
```

## Formatting

```python
format(*args, markup=None) -> str
```

Returns the same layout that `np.show` would print, but with color codes
stripped, so it can be logged to a file or embedded in another message.

```python
format_list(*args, markup=None) -> list[TextObject]
```

The lower-level pipeline. Each returned object has a
`render(color_code_scheme=...)` method, where the scheme is `'plain'`,
`'ansi'`, or `'bbcode'`. Use it when you want to post-process pieces rather
than print them directly. The remaining parameters (`_frame`,
`_elevate_parent_level`, `_mark_position`, `_raise_builtin_print`) are
internal.

### Text objects

```python
Text(obj, color='default', style='')
```

A piece of text with an explicit color and style. `True`, `False`, and `None`
are rendered green, red, and magenta by default. Colors can be names, Rich
styles, or `#rrggbb` values.

```python
Markdown(text)
```

A Rich-rendered Markdown block. Prefer `np.markdown()` for printing, which
also takes care of the markup and line break.

## Scopes and counters

```python
scope(name='') -> contextmanager
```

Opens a named scope for the `with` block. Inside it, `:i2` (and `np.index`)
counts per scope and `:t3` reports scope-level timing. Without a name, a
random short id is generated.

## Progress bars

```python
Progress(total=None, indicator_style='counter', color='red')
```

A manual progress bar. `indicator_style` is one of `'counter'`, `'digital'`,
`'decimal'`, or `'none'`; `color` is one of `'blue'`, `'green'`, `'yellow'`,
`'red'`.

Methods:

| Method | Effect |
| :----- | :----- |
| `update(item=None)` | advance one step; `item` is an optional label |
| `close()` | move to a new line and reset |
| `reset()` | reset the counter and total |
| `total` (property) | read or set the total before the first `update()` |

`total` is required for a normal bar. A `Progress` without a total raises
`NotImplementedError` on the first `update()`.

```python
progress(obj, total=None, **kwargs) -> Iterator
```

A generator that wraps an iterable and advances automatically. For concrete
sized containers, `total` is inferred from `len(obj)`; generators need an
explicit `total`.

```python
ProgressItem(data, label='')
```

Wraps one item of a `progress()` iteration to attach a label. The loop
receives `data`, and the bar shows `label` (or `str(data)` when omitted).

`Spinner` and `spinner()` are exported as reserved names and are not
implemented yet.

## Configuration

```python
config(**kwargs) -> None
config.reset() -> None
```

Change global options, or restore defaults. See
[Configuration](./configuration.md) for the full option table.

## Package control

```python
setup(package_name=None) -> None
unload() -> None
```

`np.setup(__package__)` replaces the builtin `print` with `np.print` for the
given package, so existing `print` calls gain neoprint's formatting without
being edited. `np.unload()` restores the builtin `print`.

## Advanced

| Name | Purpose |
| :--- | :------ |
| `np.console` | the underlying Rich console |
| `np.bprint` | the original builtin-style print, always unformatted |
| `np.FrameInfo` | frame inspection used by source prefixes and aliases |
| `np.elevate_parent_level` | adjust which frame is reported as the caller |
| `np.debugger` | internal debugger switch object |
| `np.text_object` | all text object classes |
