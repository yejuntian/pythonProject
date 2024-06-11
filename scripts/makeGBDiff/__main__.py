import argparse
import os
import time
from makeDiff import main as gbDiff
from others import other

"""
    主要作用：WhatsApp包制作成gbWhatsapp Diff 方便对比的总入口
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # 打包成pip脚本记得修改：isConsole=False
    # mPath = makeGBDiff.__file__
    # mCurrentPath = mPath[0:mPath.rindex("/makeGBDiff")]
    mCurrentPath = os.getcwd()
    before = time.time()
    print(f"*********** 移除{from_dir} 所有行号开始 ************")
    os.chdir(from_dir)
    # os.system("find . -name '*.smali' | xargs sed -i '' -E '/\.line[[:space:]][0-9]+/d'")
    print(f"*********** 移除{from_dir} 所有行号结束 ************")
    # 换包名
    print("*********** 由com.gbwhatsapp---->com.whatsapp 开始 ************")
    gbDiff(from_dir, mCurrentPath, isConsole=True)
    print("*********** 由com.gbwhatsapp---->com.whatsapp 结束 ************")
    # 删除无用文件夹，替换特定字符串
    print("*********** 其他操作->删除无用文件夹，替换特定字符串开始 ************")
    other(from_dir)
    print("*********** 其他操作->删除无用文件夹，替换特定字符串结束 ************")
    after = time.time()
    print(f"程序执行结束，输出结果保存到：{from_dir} 共耗时 {after - before} 秒")


if __name__ == "__main__":
    main()
