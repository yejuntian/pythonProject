import os
import re
import json
import argparse

resMapping = {}
regexStr = r"Lcom\/study\/emptyproject\/R\$(.*)\;\-\>(.*)\:I"

"""

    主要作用：查找项目中Lcom/study/emptyproject/R$xml;->cow_yo_debug_mods:I这种格式的资源，
    并把需要依赖的资源保存到GBNeedToFind.json文件中。
    
"""


def searchProjectRes(folderPath):
    startSearchRes(folderPath)
    # print(resMapping)
    save2File(f"{os.getcwd()}/scripts/values/native_values/GBNeedToFind.json", resMapping)


def save2File(folder_path, dataList):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(folder_path, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{folder_path}")


def startSearchRes(folderPath):
    listdir = os.listdir(folderPath)
    for fname in listdir:
        fpath = os.path.join(folderPath, fname)
        if os.path.isdir(fpath):
            startSearchRes(fpath)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] == "smali":
                with open(fpath, mode="r", encoding="utf-8") as rf:
                    matches = re.finditer(regexStr, rf.read(), re.MULTILINE)
                    for matchNum, match in enumerate(matches, start=1):
                        attrStyle = match.group(1)
                        attrName = match.group(2)
                        if resMapping.get(attrStyle) is None:
                            resMapping[attrStyle] = []
                        if attrName not in resMapping.get(attrStyle):
                            resMapping[attrStyle].append(attrName)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folderPath")
    args = parser.parse_args()
    folderPath = args.folderPath

    # folderPath = "/Users/shareit/work/shareit/MyInsta_v250_3400022109/DecodeCode/MyInsta_v25.0_340.0.0.22.109/smali_classes14"
    searchProjectRes(folderPath)
