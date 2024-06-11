import glob
import os
import argparse

"""
 主要作用：读取plus_targetStr文本内容，并替换plus_replaceStr目标字符串。
"""


def replaceLayout(from_dir):
    replaceStr = getData(f"{os.getcwd()}/scripts/repalce_layout/modify_plus/plus_replaceStr")
    targetStr = getData(f"{os.getcwd()}/scripts/repalce_layout/modify_plus/plus_targetStr")
    listdir = glob.glob(f"{from_dir}/*.xml", recursive=True)
    for path in listdir:
        print(path)
        with open(path, encoding='utf-8', mode='r') as rf:
            data = rf.read()
            data = data.replace(replaceStr, targetStr)
        with open(path, encoding='utf-8', mode='w') as wf:
            wf.write(data)
    print("*******程序执行结束！*******")


def getData(fpath):
    with open(fpath, encoding='utf-8', mode='r') as rf:
        return rf.read()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.11.79/DecodeCode/Whatsapp_v2.24.11.79"
    replaceLayout(f"{from_dir}/res/layout")
