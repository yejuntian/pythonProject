import codecs
import json
import os
import re

resultDict = {}
newResultDict = {}
regexList = [r"\"@(\w+)/(APKTOOL_DUMMYVAL_(\w+))\"", r"(whatsapp|app):(APKTOOL_DUMMYVAL\w+)=",
             r"\"@(\w+)\/(.*?)\"", r"\"([?])(APKTOOL_DUMMYVAL\w+)\""]
"""
    主要作用：根据from_path读取xml文件，匹配xml文件中的所有符合正则dimenRegex的属性，
    并把匹配结果保存到matchStyles/findAlldimen/result.json
"""


def findAllDimens(fpath):
    for regex in regexList:
        matchRes(fpath, regex, resultDict)

    for type, attrList in resultDict.items():
        if newResultDict.get(type) is None:
            newResultDict[type] = {}
        for attr in attrList:
            if attr.startswith("APKTOOL_DUMMYVAL_"):
                newResultDict[type][attr] = ""
    save2File(os.getcwd(), newResultDict, "result.json")
    # save2File(f"{os.getcwd()}/scripts/values/matchStyles/findAlldimen", resultDict, "result.json")


def save2File(folder_path, dataList, fileName):
    # print(dataList)
    fpath = os.path.join(folder_path, fileName)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fpath, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{fpath}")


def matchRes(fpath, regex, resultDict):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
        matches = re.finditer(regex, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=0):
            matchType = str(match.group(1))
            # print(match)
            matchValue = match.group(2)
            if resultDict.get(matchType) is None:
                resultDict[matchType] = []
            if matchValue not in resultDict[matchType]:
                resultDict[matchType].append(matchValue)


if __name__ == "__main__":
    from_path = "/Users/shareit/work/shareit/gbwhatsapp_2.24.3.81/DecodeCode/Whatsapp_v2.24.3.81/res/layout/home.xml"
    findAllDimens(from_path)
