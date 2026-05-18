# 索引计数器设计

标记符说明:

- `:i0`: 对当前作用域, 行计数器, 全局计数器均进行重置.
- `:i1`: 行计数器, 只在当前行被调用时, 计数 +1.
- `:i2`: 作用域计数器. 对当前作用域计数 +1.
- `:i3`: 全局计数器. 在任何作用域被调用时, 计数 +1.

标记符简写:

- `:i`: 等价于 `:i2`

标记符的其他写法:

```python
import neoprint as np
np.show('aaa', markup=':i')  # 等同于: np.show('aaa', ':i')
```

## 作用域

什么是作用域?

作用域是指该行代码所在的函数/类/模块, 或者自定义的作用域范围.

下面分别展示不同的作用域:

```python
# example.py
import neoprint as np

np.show(...)  # you are in __module__ scope.

def foo():
    np.show(...)  # you are in foo scope.

    def bar():
        np.show(...)  # you are in bar scope.

class Baz:
    np.show(...)  # you are in Baz scope.

with np.scope():
    np.show(...)  # you are in untitled scope.

with np.scope(name='MyScope'):
    np.show(...)  # you are in MyScope scope.
```

## 测试

见 `test/golden_test/scoped_index_counter.py`.
