import argparse
import codecs
import json
import os
import re

resultDict = {}
dimenRegex = r"\"@dimen/(APKTOOL_DUMMYVAL_\w+)\""
typeDict = {dimenRegex: "dimen"}

"""
    主要作用：根据from_path读取xml文件，匹配xml文件中的所有符合正则dimenRegex的属性，
    并把匹配结果保存到matchStyles/findAlldimen/result.json
"""


def findAllDimens(fpath):
    for regex, type in typeDict.items():
        matchRes(fpath, regex, type, resultDict)

    save2File(f"{os.getcwd()}/scripts/values/matchStyles/findAlldimen", resultDict, "result.json")


def save2File(folder_path, dataList, fileName):
    fpath = os.path.join(folder_path, fileName)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fpath, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{fpath}")


def matchRes(fpath, regex, type, resultDict):
    if resultDict.get(type) is None:
        resultDict[type] = []
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
        matches = re.finditer(regex, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            matchStr = match.group(1)
            if not matchStr in resultDict[type]:
                resultDict[type].append(matchStr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_path")
    args = parser.parse_args()
    from_path = args.from_path
    # from_path = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.2.76/res/layout/conversations_row.xml"
    findAllDimens(from_path)
