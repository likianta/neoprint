import neoprint as np

def test_exception_marker():
    print("=== Testing :e marker ===")
    try:
        x = 1 / 0
    except Exception as e:
        np.show(e, ":e0")
        print()
        np.show(e, ":e1")
        print()
        np.show(e, ":e2")
        print()
        np.error(e)
        print()


test_exception_marker()
