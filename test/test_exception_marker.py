import neoprint as np

def inner_function():
    x = 10
    y = "hello"
    result = x / 0
    return result

def outer_function():
    data = [1, 2, 3]
    inner_function()

def test_e0():
    try:
        outer_function()
    except ZeroDivisionError as e:
        print("=== :e0 (exception, short/no expand) ===")
        np.show(e, ':e0')

def test_e1():
    try:
        outer_function()
    except ZeroDivisionError as e:
        print("\n=== :e1 (exception, long format) ===")
        np.show(e, ':e1')

def test_e2():
    try:
        outer_function()
    except ZeroDivisionError as e:
        print("\n=== :e2 (exception, long format with locals) ===")
        np.show(e, ':e2')

if __name__ == '__main__':
    test_e0()
    test_e1()
    test_e2()
