# 日志级别与颜色

| mark | level | color |
| ---- | ----- | ----- |
| `:v0` | N/A  | No ANSI color |
| `:v1` | DEBUG | bright_black |
| `:v2` | INFO | cyan |
| `:v3` | WEAK SUCCESS | dim green |
| `:v4` | SUCCESS | green |
| `:v5` | WEAK WARNING | dim yellow |
| `:v6` | WARNING | yellow |
| `:v7` | WEAK ERROR | dim red |
| `:v8` | ERROR | red |
| `:v9` | CRITICAL | white text on red background |

助记: `:v1/3/5/7` 是弱信息, 用黯淡的颜色; `:v2/4/6/8` 是强信息, 用明亮的颜色; `:v0` 和 `:v9` 比较特殊, 一个是无日志级别, 不使用 ANSI 颜色, 另一个是严重错误, 用强烈的引入注意的颜色.

简写: `:v` 等价于 `:v1`.

## 相关测试

- `test/golden_test/verbosity_levels.py`
