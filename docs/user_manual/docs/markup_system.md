# How Markup Works

Neoprint keeps the `print` signature. Instead of adding dozens of keyword
arguments, it adds one optional string — the **markup** — that switches
features on.

## Grammar

A markup starts with `:` and is a concatenation of mark *letters*, each
optionally followed by a single digit:

```text
:n          one mark, default variant
:v8          one mark, variant 8
:i0         reset the index counter
:d2v7t      three marks combined
```

The valid letters are `d`, `e`, `f`, `i`, `l`, `n`, `p`, `r`, `s`, `t`, `v`.
Digits are `0`-`9`.

A string is only treated as a markup when it matches this grammar exactly and
is in the first or last positional slot (or passed via `markup=`). Otherwise it
is printed literally, so ordinary text like `':'` or `':)'` never gets
misinterpreted.

## What a mark can change

Every mark affects one of three layers of the output:

| Layer | Marks | Examples |
| :---- | :---- | :------- |
| The **head** (left of the separator) | `p` | show the caller of the caller |
| The **prefix** inside the body | `i`, `t` | `[3]` index, `[12:00 -> 12:01 (1m)]` timing |
| The **values and layout** | `d`, `e`, `l`, `n`, `r`, `s`, `v` | colors, tables, dividers, tracebacks |

## Order of marks does not matter

`:tiv2` and `:v2it` are the same markup. What matters is the position inside
the call, and the digits.

## Some pairs conflict

- `:d` (divider style) and `:l` (expanded format) cannot be used together.
  A divider wraps the body in a single line, an expanded format spreads it over
  many; neoprint rejects that combination with an `AssertionError`.
- `:r2` and `:l2` mean the same thing. When both are given, the `:l` one is
  kept.
- `:d` overrides `:r2` by turning it off.

When in doubt, enable one layout mark at a time.

## Marks are per call

Marks do not stick. `np.show('x', ':v8')` prints one red line; the next call
starts from the defaults again. The only stateful features are the index
counters (`:i`) and timers (`:t`), and they have explicit reset marks
(`:i0`, `:t0`).

## Where to go next

- [Markup Reference](./markup_reference.md) — every mark, every variant.
- Individual guides under **Guides** explain each feature in depth.
