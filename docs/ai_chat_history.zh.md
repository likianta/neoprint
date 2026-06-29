### 2026-06-24

请先阅读 `./test/bbcode_to_ansi.py` 脚本, 完成 `./neoprint/render.py:translate` 函数, 并通过此测试.

### 2026-06-25

请完成此函数: `./neoprint/util.py:ansi_to_bbcode`, 并在 `./test/show_varnames.py` 中查看打印效果.

---

我想扩展 show_varnames (`:n`) 的解析范围. 之前 `:n` 只能识别 `ast.Name` (见 `./neoprint/sourcemap.py:VarnamesAnalyzer:visit_Call`), 现在, 我想让 `ast.Call` 也被识别.

示意代码:

```python
# before
np.show(name, len(name), ':n')  # -> name = "Alice"; 5
# after
np.show(name, len(name), ':n')  # -> name = "Alice"; len(name) = 5
```

请完成该功能, 并在 `./test/show_varnames.py` 中验证.

---

请为本项目撰写一个 README.md 文件. 要求如下:

- 你需要先阅读我自己编写的文档 (`./docs/mdbook.zh/src`) 以及源代码 (`./neoprint`), 对该项目有比较全面且深入的了解.
- 使用英文书写 README.md.
- 不需要写得太详细, 着重介绍这个项目是做什么的, 怎么安装, 以及怎么快速开始使用 (参考 `./examples/all_markup_usage.py`).
- 不需要介绍比较深入的概念, 比如 `:p` 机制, `np.format_list` ... 这些都不要介绍.
- 使用丰富的截图. 你可以留下占位符 (`TODO(Image): <Note>`, 例如 "TODO(Image): Record a GIF to show the progress effect"). 之后我会手动配图.
- 你可以参考 `./human/prototype/README.md` -- 这是另一个项目的文档, 但具有非常重要的参考价值.

为了方便你开始, 我给你提供了下面的模板:

```md
# Neoprint

<pypi_badge>

<quick_introduction>

TODO(Image): Main picture of this tool.

## Features

...

## Installation

...

## Quick Start

### Hello world

...

### Print with varnames

...

### Highlighting and verbosity levels

...

### Indexing and timing

...

### Progress

...

### <more_usages>

...

## Markup Feature

<table, see also `./docs/mdbook.zh/src/markup_list.md`>

...

## Screenshots

...
```

### 2026-06-29

我要使用 `:e` 标记来追踪和漂亮地打印错误堆栈信息.

当前 `:e` 标记值定义:

- `:e0`: 不使用错误堆栈打印 (按照常规打印风格继续).
- `:e1`: 以红色文字显示 `str(e)` 的内容.
- `:e2` (默认): 以 rich traceback panel 风格显示打印.
- `:e3`: 与 `:e2` 类似, 但是显示更多信息 (show_locals=True)

请参考以下代码完成该功能:

- `./docs/mdbook.zh/src/markup_list.md`: 标记含义说明.
- `./neoprint/config.py:_Config:_custom_excepthook`: 展示了 rich.traceback 的用法, 可作为参考.
- `./neoprint/console.py:_LegacyRichConsole:capture_output` 和 `./neoprint/text_object/rich.py:RichObject`: 展示了如何捕获 rich.print 并转化为 neoprint TextObject 对象.
- `./neoprint/markup.py:MarkupAnalyzer:extract`: 当识别到 ":e" 标记时, 其默认值为 2.
- `./neoprint/format.py:format_list`: 有一个 TODO 标记, 需要完成.
- `./neoprint/text_object/exception.py`: 待完成.
- `./test/traceback_exception.py`: 完成上述功能后, 需要通过本测试.

