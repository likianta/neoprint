# 进度条打印

进度条分为推进式和不定式两种类型.

效果示意图:

...

## 典型用法

```python
import neoprint as np
from faker import Faker
from time import sleep

fk = Faker()

# ---
np.show('Use `np.Progress` with `with` statement', ':i')
names = tuple(fk.name() for _ in range(100))
with np.Progress(total=len(names)) as p:
    for name in names:
        p.update(name)
        sleep(0.03)

# ---
np.show('Function call', ':i')
for name in np.progress(names):
    sleep(0.03)
# note: `np.progress` won't print each name in progress bar, unless you wrap 
# your value with `np.ProgressItem`.
for name in np.progress([np.ProgressItem(name) for name in names]):
    sleep(0.03)

# ---
np.show('Spinning around a generator', ':i')
def foo():
    for name in names:
        yield np.ProgressItem(name)
        sleep(0.03)
for i, name in enumerate(np.progress(foo())):
    assert name == names[i]
```

## 推进式进度条

推进式进度条必须设置 `total` 属性. 你可以在实例化时传入, 也可以在第一次 `update` 之前设置:

```python
import neoprint as np

# a.
with np.Progress(total=...) as p:
    for item in (...):
        p.update(...)
        ...

# b.
with np.Progress() as p:
    p.total = ...
    for item in (...):
        p.update(...)
        ...
```

在 `update` 之前, 你可以多次修改 `total` 属性; 在 `update` 之后, 再去设置会报错.

如果直到第一次 `update` 时, 仍未设置 `total` 属性, `neoprint.config.strict=True` 情况下会报错, 非严格模式则会自动转变为不定式进度条. (注: 默认为非严格模式.)

## 不定式进度条

...

## 高级特性

### 在进度条显示期间, 打印其他消息

...

## 特定情况讨论

### 如果 index 超过了 total, 会发生什么?

...

## 尝试一下

```shell
python examples/progress.py
```
