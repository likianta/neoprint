import neoprint as np

def inner_function():
    x = 10
    y = "hello"
    result = x / 0
    return result

def outer_function():
    data = [1, 2, 3]
    inner_function()

def test_rich_traceback_without_locals():
    try:
        outer_function()
    except ZeroDivisionError as e:
        print("=== :v8l (expand with traceback, no locals) ===")
        np.show(e, ':v8l')

def test_rich_traceback_with_locals():
    try:
        outer_function()
    except ZeroDivisionError as e:
        print("\n=== :v8l2 (expand with traceback and locals) ===")
        np.show(e, ':v8l2')

def test_normal_error():
    try:
        outer_function()
    except ZeroDivisionError as e:
        print("\n=== :v8 (normal error) ===")
        np.show(e, ':v8')

if __name__ == '__main__':
    test_rich_traceback_without_locals()
    test_rich_traceback_with_locals()
    test_normal_error()
