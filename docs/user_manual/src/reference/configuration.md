# Configuration

Global switches live in a single object, `np.config`. Call it with keyword
arguments to change settings, and `np.config.reset()` to restore defaults.

```python
import neoprint as np

np.config(show_varnames=True)
...
np.config.reset()
```

Unknown names raise `AssertionError`, which catches typos early.

## Options

| Option | Default | Effect |
| :----- | :------ | :----- |
| `show_source` | `True` | show the `filename:lineno` head |
| `show_varnames` | `False` | always show variable names, as if `:n` were passed |
| `disable_varnames` | `False` | never show variable names, and skip source parsing |
| `console_width` | terminal width | width used for dividers, progress bars, wrapping |
| `multiline_indent` | `2` | spaces per nesting level in expanded output |
| `legacy_windows` | `False` | reduce color effects on legacy consoles |
| `rich_traceback` | `True` | install Rich's excepthook for uncaught exceptions |
| `show_traceback_locals` | `False` | include locals in uncaught-exception panels |
| `sourcemap_alignment` | `'left'` | pad line numbers so heads align |
| `debug_print` | `False` | verbose internal logging of neoprint itself |
| `debug_output` | `False` | collect printed output for tests |

A few options are accepted but have no visible effect yet: `show_funcname`,
`show_verbosity_tag`, `path_style`, `clear_unfinished_stream`, `subthreaded`.
They are reserved for upcoming releases.

## Environment variables

Some switches can be set before the interpreter imports neoprint:

| Variable | Equivalent |
| :------- | :--------- |
| `NEOPRINT_DEBUG=1` | `debug_print=True` |
| `NEOPRINT_DEBUG_PRINT=1` | `debug_print=True` |
| `NEOPRINT_DISABLE_VARNAMES=1` | `disable_varnames=True` |
| `NEOPRINT_LEGACY_WINDOWS=1` | `legacy_windows=True` |

This is useful for CI, where you may want to disable variable-name lookups
without touching the code. Note that `console_width` has no environment
variable; set it from code with `np.config(console_width=100)`.

## A typical setup

```python
import neoprint as np

# a wide, stable layout in CI, verbose helpers locally
np.config(
    console_width=120,
    multiline_indent=2,
    show_varnames=True,
)
```

## Debugging neoprint itself

`debug_print=True` makes neoprint narrate its own decisions (frame resolution,
markup analysis, varname lookups) to stderr. It is meant for reporting bugs,
not for daily use.
