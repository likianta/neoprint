# 标记符用法

## `:l` 标记符

- `:l0`: 不启用
- `:l1`: 对可打印对象进行多行展开 (类似于 pprint.pformat 效果), 特别地, 对于 `Exception` 对象, 使用类似 `traceback.format_exc` 的格式.
- `:l2`:

    对可打印对象进行专门的排版.

    目前支持的特殊对象有:

    - `List[Sequence[str]]`: 排版为表格.
    - `Dict[str, str]`: 排版为键值对表格.
    - 符合特定格式的字符串 (使用正则表达式识别):
        - `AAA -> BBB`: 渲染为 `[red]AAA[/] -> [green]BBB[/]`
        - `CCC: DDD -> EEE`: 渲染为 `CCC: [red]DDD[/] -> [green]EEE[/]`

    不符合以上对象的, 会按照 `:l1` 风格格式化.

简写: `:l1` 可简写为 `:l`.

效果示意代码:

```python
import neoprint as np
import os

names = os.listdir(...)

np.show(names, ':l0')
# -> example.py:6   | ['AAA', 'BBB', 'CCC', 'DDD', ...]

np.show(names, ':l1')
"""
output illustration:
    example.py:9   | 
        [
            "AAA",
            "BBB",
            "CCC",
            "DDD",
            ...
        ]
"""

np.show(
    ':l2', 
    [
        ('index', 'name', 'age', 'city'),
        ('1', 'AAA', '20', 'New York'),
        ('2', 'BBB', '24', 'Los Angeles'),
        ('3', 'CCC', '30', 'Chicago'),
    ],
    'v0.1.0 -> v0.2.0',
    {
        'name': 'neoprint',
        'version': '0.1.0',
        'author': 'Likianta',
    }
)
"""
output illustration:
    example.py:22  | 
        | index | name | age | city        |
        | ----- | ---- | --- | ----------- |
        | 1     | AAA  | 20  | New York    |
        | 2     | BBB  | 24  | Los Angeles |
        | 3     | CCC  | 30  | Chicago     |
        
        [red]v0.1.0[/] -> [green]v0.2.0[/]
        
        | name    | neoprint |
        | version | 0.1.0    |
        | author  | Likianta |
"""
```

注: `:l3` 注释中的 `[red]v0.1.0[/] -> [green]v0.2.0[/]` 需要用 ANSI 颜色代码渲染.
