# Markup Reference

One table, every mark. The **Default** column marks the variant used when the
letter is written without a digit (`*` = the bare form selects this variant).

## Divider `d`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:d0` | no divider |
| * | `:d1` | thin divider line |
|   | `:d2` | thick divider line |

See [Dividers](./guides/dividers.md).

## Exception `e`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:e0` | no special handling; print as ordinary value |
|   | `:e1` | print the exception message in red |
| * | `:e2` | Rich traceback panel |
|   | `:e3` | Rich traceback panel with locals (`show_locals`) |
|   | `:e4` | reserved, not implemented |

See [Exception Printing](./guides/exception.md).

## Flush `f`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
| * | `:f1` | reserved |

The `f` mark is parsed for forward compatibility but currently has no effect on
the output. Do not rely on it.

## Index `i`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:i0` | reset counters |
| * | `:i1` | line-level counter (one counter per source line) |
|   | `:i2` | scoped counter (per function, or per `np.scope`) |
|   | `:i3` | global counter |

See [Index Counters](./guides/index_counter.md).

## Layout `l`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:l0` | inline representation |
| * | `:l1` | expand containers over multiple lines |
|   | `:l2` | tailored layout (tables, key-value grids, `a -> b` transforms) |

See [Expanded Formatting](./guides/expanded_format.md).

## Varnames `n`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:n0` | hide variable names |
| * | `:n1` | show variable names and expressions |

See [Variable Names](./guides/varnames.md).

## Parent layer `p`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:p0` | head points at the current frame |
| * | `:p1` | head points at the caller |
|   | `:p2` | caller's caller |
|   | `:p3`+ | one frame further up per number |

See [Source Layers](./guides/parent_layer.md).

## Rich text `r`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:r0` | inline markup disabled |
| * | `:r1` | inline markup enabled (`[red]...[/]`) |
|   | `:r2` | same as `:l2` |

See [Rich Text](./guides/rich_text.md).

## Short `s`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:s0` | full output |
| * | `:s1` | short form: no source head, no variable names |
|   | `:s2` | delegate to the built-in `print` |

See [Printing Basics](./basic_usage.md#quiet-and-plain-modes).

## Timing `t`

| Default | Mark | Description |
| :-----: | :--- | :---------- |
|   | `:t0` | reset the timer |
|   | `:t1` | absolute timestamp |
| * | `:t2` | time since the previous `:t2`/`:t3` call |
|   | `:t3` | time since the scope timer was reset |

See [Timing](./guides/timing.md).

## Verbosity `v`

| Default | Mark | Description | Color |
| :-----: | :--- | :---------- | :---- |
| * | `:v0` | debug | gray |
|   | `:v1` | negative info | magenta |
|   | `:v2` | positive info | blue |
|   | `:v3` | weak success | dim green |
|   | `:v4` | success | green |
|   | `:v5` | weak warning | dim yellow |
|   | `:v6` | warning | yellow |
|   | `:v7` | weak error | dim red |
|   | `:v8` | error | red |
|   | `:v9` | critical | reserved, not implemented |

See [Verbosity Levels](./guides/verbosity.md).
