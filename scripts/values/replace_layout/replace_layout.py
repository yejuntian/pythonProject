import codecs
import json
import argparse
import os

# 只匹配下面的文件类型
extends = ["xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']
# 存储对应关系文件
dataPath = 'scripts/values/replace_layout/layout.json'

"""
    主要作用：根据layout.json中对应关系，
    替换项目所涉及的res/layout目录下的xml布局文件名
"""


def load_replace_keys(dataPath):
    with codecs.open(dataPath, "r", "utf-8") as rfile:
        return json.loads(rfile.read())


def execute_folder(from_dir, blacklist, extends, mapping_string):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        if fname not in blacklist:
            fpath = os.path.join(from_dir, fname)
            if os.path.isdir(fpath):
                execute_folder(fpath, blacklist, extends, mapping_string)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends:
                    print(fpath)
                    save_2_file(fpath, fname, from_dir)


def save_2_file(fpath, fname, from_dir):
    enableRenameFile = False
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        data = rf.read()
    with codecs.open(fpath, mode="w", encoding="utf-8") as wf:
        replace_times = 0
        for key, value in mapping_string.items():
            if key.startswith("APKTOOL_DUMMYVAL_"):
                replace_times += data.count(key)
                data = data.replace(key, value)
                if key == fname.split(".")[0]:
                    enableRenameFile = True
                    newPath = os.path.join(from_dir, f"{value}.xml")
        print(r'替换次数：', replace_times)
        wf.write(data)
    if enableRenameFile:
        # # 解决重复发执行脚本，对重命名的文件进行还原
        # if os.path.exists(newPath):
        #     os.rename(newPath, fpath)
        os.rename(fpath, newPath)


if __name__ == '__main__':
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.22.24.78"
    mapping_string = load_replace_keys(f"{mCurrentPath}/{dataPath}")
    execute_folder(from_dir, blacklist, extends, mapping_string)
