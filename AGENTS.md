# Neoprint

## 这是一个什么项目

本工具用于打印对象到控制台, 相较于 Python 内置的 `print` 函数, 本工具提供更具表达力的输出效果.

特性:

- 终端输出带颜色的文本
- 进度条动画
- 漂亮地格式化对象
- 附带显示更多关联信息 (源码位置, 变量名称, 计数器, 计时器等)

## 项目目录结构

- .venv: Python 虚拟环境. 使用 uv 创建, Python 版本为 3.14.
- neoprint: 源代码.
- docs/mdbook.zh: 与本项目有关的各类知识及备忘. 以中文作为主要语言.
- examples: 示例代码.
- test: 在这里编写各类验证脚本.

## 工具链

- 使用 `python` 运行脚本.
- 使用 `uv` 管理 pyproject.toml 中的依赖.
- 使用 `ty` 检查类型错误.
- 使用 `ruff` 格式化代码.

## 代码风格

- 优先使用 `format` 而不是 `f-string`.
- 代码中使用全英文, 不要有中文注释.
- 不需要在入口脚本的顶部添加 `sys.path.append(...)`. 因为我们已经设置好了环境变量 `PYTHONPATH=.;src;lib;.venv/Lib/site-packages`.
- 每行代码不超过 80 字符 (见 `pyproject.toml:[tool.ruff]:line-length`).
- 每当完成修改后, 使用 `ty check`, `ruff check`, `ruff format` 等命令检查代码风格.

