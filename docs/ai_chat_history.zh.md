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

