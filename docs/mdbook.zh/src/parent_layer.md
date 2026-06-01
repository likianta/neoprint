# 打印层级

## 层级的含义

neoprint 默认打印会包含 `{filename}:{lineno}`, 这个信息与调用者的层级相关. 我们通过改变层级参数来改变输出的信息头.

层级一共支持 `:p0` 到 `:p9` 共 10 层, 依次表示当前调用者 (`np.show` 所在行), 调用者的调用者, 调用者的调用者的调用者... 

通过示例来理解:

```python
# example.py
import neoprint as np  # ln1

def aaa():  # ln3
    def bbb():  # ln4
        def ccc():  # ln5
            def ddd():  # ln6
                np.show('DDD', ':p0')  # ln7
                np.show('CCC', ':p1')  # ln8
                np.show('BBB', ':p2')  # ln9
                np.show('AAA', ':p3')  # ln10
                np.show('<module>', ':p4')  # ln11
                np.show('???', ':p5')  # ln12
            ddd()  # ln13
        ccc()  # ln14
    bbb()  # ln15
aaa()  # ln16

# output:
#   example.py:7   | DDD
#   example.py:13  | CCC
#   example.py:14  | BBB
#   example.py:15  | AAA
#   example.py:16  | <module>
#   Error: `:p5` is out of stack.
```

## 层级的作用

当存在一个公共函数, 会被多个来源调起时, 我们用 `:p` 来 "追踪" 每个调用者的来源:

```python
import neoprint as np

class Library:
    def borrow_book(self, book_name):
        np.show(f'borrowed "{book_name}"', ':p')
        return Book(book_name)

lib = Library()

# in aaa.py
lib.borrow_book('How the Steel Was Termpered')

# in bbb.py
lib.borrow_book('Stray Birds')

# --- output
#   aaa.py:23  | borrowed "How the Steel Was Termpered"
#   bbb.py:10  | borrowed "Stray Birds"
```

这方便我们查阅信息, 更好地理解信息, 以及调试代码.
