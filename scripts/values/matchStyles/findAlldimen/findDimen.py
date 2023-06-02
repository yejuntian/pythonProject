import argparse
import codecs
import json
import os
import re

resultDict = {}
dimenRegex = r"\"@(\w+)/(APKTOOL_DUMMYVAL_\w+)\""

"""
    主要作用：根据from_path读取xml文件，匹配xml文件中的所有符合正则dimenRegex的属性，
    并把匹配结果保存到matchStyles/findAlldimen/result.json
"""


def findAllDimens(fpath):
    matchRes(fpath, dimenRegex, resultDict)
    save2File(f"{os.getcwd()}/scripts/values/matchStyles/findAlldimen", resultDict, "result.json")


def save2File(folder_path, dataList, fileName):
    print(dataList)
    fpath = os.path.join(folder_path, fileName)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fpath, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{fpath}")


def matchRes(fpath, regex, resultDict):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
        matches = re.finditer(regex, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            matchType = str(match.group(1))
            matchValue = match.group(2)
            if resultDict.get(matchType) is None:
                resultDict[matchType] = []
            if not matchValue in resultDict[matchType]:
                resultDict[matchType].append(matchValue)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_path")
    args = parser.parse_args()
    from_path = args.from_path
    # from_path = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.2.76/res/layout/conversations_row.xml"
    findAllDimens(from_path)
