import neoprint as np
import traceback

def main():
    try:
        np.debug.enabled = True
        # Try :p1000, which should be way beyond the stack depth
        np.show(':p1000', 'Testing :p that goes too far')
        print("Test failed: Did not get an error as expected!")
        return False
    except Exception as e:
        print(f"Test passed! Got expected error: {type(e).__name__}: {e}")
        print(f"Stack trace:")
        traceback.print_exc()
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
