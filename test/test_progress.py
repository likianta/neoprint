import neoprint as np
from time import sleep


def test_basic_progress():
    print("=== 测试基本进度条功能 (counter 样式)...")
    with np.Progress(total=20) as prog:
        for i in range(20):
            prog.update(f"步骤 {i+1}")
            sleep(0.05)
    print("✓ 基本进度条测试完成！\n")


def test_digital_progress():
    print("=== 测试 digital 样式进度条...")
    with np.Progress(total=50, indicator_style='digital') as prog:
        for i in range(50):
            prog.update(f"正在处理 {i+1}/50")
            sleep(0.02)
    print("✓ digital 样式进度条测试完成！\n")


def test_decimal_progress():
    print("=== 测试 decimal 样式进度条...")
    with np.Progress(total=30, indicator_style='decimal') as prog:
        for i in range(30):
            prog.update(f"进度 {i+1}/30")
            sleep(0.03)
    print("✓ decimal 样式进度条测试完成！\n")


def test_none_indicator_progress():
    print("=== 测试 none 样式进度条（无指示器）...")
    with np.Progress(total=15, indicator_style='none') as prog:
        for i in range(15):
            prog.update(f"处理 {i+1}")
            sleep(0.04)
    print("✓ none 样式进度条测试完成！\n")


def test_spinner():
    print("=== 测试 spinner 动画（无 total）...")
    with np.Progress() as prog:
        for i in range(30):
            prog.update(f"正在加载...  步骤 {i+1}")
            sleep(0.05)
    print("✓ spinner 测试完成！\n")


def test_debug_mode():
    print("=== 测试调试模式（逐行输出）...")
    np.debugger.enabled = True
    with np.Progress(total=5) as prog:
        for i in range(5):
            prog.update(f"调试模式 {i+1}")
            sleep(0.1)
    np.debugger.enabled = False
    print("✓ 调试模式测试完成！\n")


def test_long_text_truncation():
    print("=== 测试长文本截断功能...")
    long_text = "这是一段非常长的文本，用来测试进度条在文本超出控制台宽度时的自动截断功能，确保显示效果美观。" * 5
    with np.Progress(total=10) as prog:
        for i in range(10):
            prog.update(f"{long_text} - {i+1}")
            sleep(0.05)
    print("✓ 长文本截断测试完成！\n")


def test_set_total_before_update():
    print("=== 测试在 update() 之前设置 total...")
    prog = np.Progress()
    prog.total = 10  # 在 update() 之前设置
    with prog:
        for i in range(10):
            prog.update(f"测试设置 total {i+1}")
            sleep(0.05)
    print("✓ 在 update() 之前设置 total 测试完成！\n")


def test_error_after_update_then_set_total():
    print("=== 测试在 update() 之后设置 total（应该报错）...")
    try:
        prog = np.Progress()
        prog.update("第一次更新")
        prog.total = 20  # 这个应该会报错
        print("✗ 错误：没有抛出异常！")
    except ValueError as e:
        print(f"✓ 正确抛出异常：{e}")
    print()


if __name__ == '__main__':
    print("开始进度条功能测试套件\n")
    
    test_basic_progress()
    test_digital_progress()
    test_decimal_progress()
    test_none_indicator_progress()
    test_spinner()
    test_debug_mode()
    test_long_text_truncation()
    test_set_total_before_update()
    test_error_after_update_then_set_total()
    
    print("所有测试完成！")
