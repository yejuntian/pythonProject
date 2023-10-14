import codecs
import json
import argparse
import xml.etree.ElementTree as ET
import os

# 只匹配下面的文件类型
extends = ["xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']
# 存储对应关系文件
dataPath = 'scripts/values/replace_layout/layout.json'
# 保存public.xml对应关系
publicTypeDic = {}
publicIdDic = {}
# 用于存放重复的属性名称
repeatName = {}
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
                    save_2_file(fpath, fname, from_dir, mapping_string)


def save_2_file(fpath, fname, from_dir, mapping_string):
    enableRenameFile = False
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        data = rf.read()
    with codecs.open(fpath, mode="w", encoding="utf-8") as wf:
        replace_times = 0
        for key, value in mapping_string.items():
            if key.startswith("APKTOOL_DUMMYVAL_") and not value == "":
                # 重命名之前，判断是否已存在重命名后的属性名称
                attrType = publicIdDic.get(key)
                attrNameList = publicTypeDic.get(attrType)
                # 判断重命名后的属性不存在,再进行重命名操作
                if attrNameList is None or value not in attrNameList:
                    replace_times += data.count(key)
                    data = data.replace(key, value)
                    if key == fname.split(".")[0]:
                        enableRenameFile = True
                        newPath = os.path.join(from_dir, f"{value}.xml")
                else:
                    # 存放重复的属性key
                    repeatName[value] = attrType
        print(r'替换次数：', replace_times)
        wf.write(data)
    if enableRenameFile:
        os.rename(fpath, newPath)


def main(mCurrentPath, from_dir):
    mapping_string = load_replace_keys(f"{mCurrentPath}/{dataPath}")
    parserPublicXml(f"{from_dir}/res/values/public.xml")
    execute_folder(from_dir, blacklist, extends, mapping_string)
    if len(repeatName) > 0:
        print("****************重复的属性名称如下：****************")
        print(repeatName)


# 解析public.xml
def parserPublicXml(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        attrId = attrib.get("id")
        if attrType is None or attrName is None:
            continue
        if publicTypeDic.get(attrType) is None:
            publicTypeDic[attrType] = []
        else:
            publicTypeDic[attrType].append(attrName)
        # 保存name和type的对应关系
        if attrName.startswith("APKTOOL_DUMMYVAL_0x7f"):
            publicIdDic[attrName] = attrType


if __name__ == '__main__':
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.22.24.78"
    main(mCurrentPath, from_dir)
