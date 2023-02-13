import argparse
import codecs
import json
import os
import re

baseVersion = "2.22.22.80"
newVersion = "2.23.2.76"

# 只匹配类eg:LX/1LM;
classRegex = r"LX/\w*;"
# 只匹配字段名eg:LX/0pE;->A10:LX/1LM; 匹配结果：->A10
filedRegex = r"L.*;(->.*):.*"
# 只匹配方法名eg:LX/0nx;->A01(Ljava/lang/String;)LX/0nx; 匹配结果：->A01
methodRegex = r"L.*/.*;(->.*)\(.*?\).+"

"""
    主要作用：根据class.json、field.json、method.json文件中的映射关系，
    对指定目录根据字符串映射关系，进行替换。
    特别注意：方法参数个数变化的需要手动进行替换，否则会出错
"""


def load_json_data(file_path):
    with codecs.open(file_path, "r", "utf-8") as rfile:
        data = rfile.read()
    return json.loads(data)


def replace_x(folder_path, mappingData, isReplaceClass):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for fileName in dirs:
        file_path = os.path.join(cwd, fileName)
        if os.path.isfile(file_path) and file_path.split('.')[-1] == "smali":
            with codecs.open(file_path, "r", "utf-8") as rfile:
                lines = rfile.readlines()
            with codecs.open(file_path, "w", "utf-8") as wfile:
                data = getReplaceResult(lines, mappingData, fileName, isReplaceClass)
                wfile.write(data)

        elif os.path.isdir(file_path):
            replace_x(file_path, mappingData, isReplaceClass)


def getReplaceResult(lines, mappingData, fileName, isReplaceClass):
    replace_times = 0
    result = ""
    regex = r"->[\w<>]+"
    for index, line in enumerate(lines):
        if not isReplaceClass:
            # 替换Filed属性
            matches = re.finditer(filedRegex, line, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                filedStr = match.group()
                if filedStr in mappingData.keys():
                    newFieldValue = getNewStr(mappingData.get(filedStr), regex)
                    # print(f"oldFiled = {match.group(1)} newFiled = {newFieldValue}")
                    line = line.replace(match.group(1), newFieldValue)
                    replace_times += 1
            # 替换method方法
            matches = re.finditer(methodRegex, line, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                methodStr = match.group()
                if methodStr in mappingData.keys():
                    newMethodValue = getNewStr(mappingData.get(methodStr), regex)
                    line = line.replace(match.group(1), newMethodValue)
                    # print(f"oldMethod = {match.group(1)} newMethod = {newMethodValue}")
                    replace_times += 1
        else:
            # 替换class
            matches = re.finditer(classRegex, line, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                classStr = match.group()
                if classStr in mappingData.keys():
                    line = line.replace(classStr, mappingData.get(classStr))
                    replace_times += 1
        result += line
    print(fr'fileName: {fileName} 替换次数：{replace_times}')
    return result


def getNewStr(str, regex):
    matches = re.finditer(regex, str, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        str = match.group()
    return str


# 组装数据
def merge_data(class_data, method_data):
    for class_item in class_data:
        old_class = class_item[baseVersion]
        for item in method_data:
            item_class = item[baseVersion]
            item_class2 = item[newVersion]
            if old_class == item_class.split("->")[0]:
                class_item[newVersion] = item_class2.split("->")[0]
                continue
    return class_data


def getOrderData(dataList):
    """有些value值和key值相同所以会导致重复替换 比如{A:B,B:C,C:D}
     A先替换为B,B替换成了C,C替换为D, 最后导致A替换成了D；
     如果调换顺序就不会发行该种情况,从字典中移除再进行逆序添加"""

    # 把所有list映射为字典
    mappingData = {}
    for item in dataList:
        key = item[baseVersion]
        value = item[newVersion]
        mappingData[key] = value

    newMappingData = mappingData.copy()

    tempList = []
    for item in dataList:
        key = item[baseVersion]
        value = item[newVersion]
        # 查找value值和key值相同,同时避免key和value相同的情况
        if value in mappingData.keys() and key != value:
            tempList.append(key)
    # 删除value值和key值相同的映射关系
    for item in tempList:
        mappingData.pop(item)
    # 进行顺序调整,逆序遍历进行添加
    tempList.reverse()
    for item in tempList:
        value = newMappingData[item]
        mappingData[item] = value
    return mappingData


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    mCurPath = os.getcwd()
    # 替换属性和方法
    method_data = load_json_data(f"{mCurPath}/scripts/findX/method.json")
    filed_data = load_json_data(f"{mCurPath}/scripts/findX/field.json")
    method_data.extend(filed_data)
    method_data = getOrderData(method_data)
    replace_x(args.from_dir, method_data, False)
    # 替换类
    class_data = load_json_data(f"{mCurPath}/scripts/findX/class.json")
    class_data = getOrderData(class_data)
    replace_x(args.from_dir, class_data, True)
