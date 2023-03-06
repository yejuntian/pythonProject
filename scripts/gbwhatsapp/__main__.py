import argparse
import os
import time
from androidx_2_androidy.convert_androidy import convertAndroidY
from gbwhatsapp_2_whatsapp.convert_gb import convertGB
from insertcode.getYoSig import sign
from insertcode.md_and_sec import sign as signMd5
from others.others import other
from public_sort.public_sort import sort
from replace_package import replacePackage
from support_2_supporty.convert_supporty import convertSupportY

"""
 主要作用：把WhatsApp转为gbWhatsapp的入口程序
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # mPath = gbwhatsapp.__file__
    # mCurrentPath = mPath[0:mPath.rindex("/gbwhatsapp")]
    mCurrentPath = os.getcwd()
    before = time.time()
    print(f"*********** 移除{from_dir} 所有行号开始 ************")
    os.chdir(from_dir)
    os.system("find . -name '*.smali' | xargs sed -i '' -E '/\.line[[:space:]][0-9]+/d'")
    print(f"*********** 移除{from_dir} 所有行号结束 ************")
    # 换包名
    print("*********** com.whatsapp--》com.gbwhatsapp换包开始 ************")
    replacePackage(from_dir)
    print("*********** com.whatsapp--》com.gbwhatsapp换包结束 ************")
    # 由gbwhatsapp-->whatsapp
    print("*********** gbwhatsapp classes back to whatsapp开始 ************")
    convertGB(from_dir, mCurrentPath)
    print("*********** gbwhatsapp classes back to whatsapp结束 ************")
    # androidx_2_androidy
    print("*********** androidx_2_androidy开始 ************")
    convertAndroidY(from_dir)
    print("*********** androidx_2_androidy结束 ************")
    # support_2_supporty
    print("*********** support_2_supporty开始 ************")
    convertSupportY(from_dir)
    print("*********** support_2_supporty结束 ************")
    # 插入签名校验
    print("*********** 插入签名校验开始 ************")
    sign(from_dir)
    signMd5(from_dir)
    print("*********** 插入签名校验结束 ************")
    sort(from_dir)
    # 其他操作->删除无用文件夹，替换特定字符串
    print("*********** 其他操作->删除无用文件夹，替换特定字符串开始 ************")
    other(from_dir, mCurrentPath)
    print("*********** 其他操作->删除无用文件夹，替换特定字符串结束 ************")
    after = time.time()
    print(f"程序执行结束，输出结果保存到：{from_dir} 共耗时 {after - before} 秒")


if __name__ == "__main__":
    main()
