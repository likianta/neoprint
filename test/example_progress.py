import neoprint as np
from time import sleep


def main():
    print("=== 进度条示例演示 ===\n")
    
    # 基本用法
    with np.Progress(total=20) as prog:
        for i in range(20):
            prog.update(f"处理中... {i+1}/20")
            sleep(0.1)
    
    print("\n✅ 进度条示例完成！")


if __name__ == "__main__":
    main()
