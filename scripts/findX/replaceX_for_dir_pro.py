import argparse
import codecs
import json
import os
import re
from baseVersion import baseVersion, newVersion

# 定义正则表达式模式
pattern = r"LX/\w*;"
isPlus = False


def load_json_data(file_path):
    with codecs.open(file_path, "r", "utf-8") as rfile:
        data = rfile.read()
    return json.loads(data)


def replace_x(folder_path, mappingData):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for fileName in dirs:
        file_path = os.path.join(cwd, fileName)
        if os.path.isfile(file_path) and file_path.split('.')[-1] == "smali":
            with codecs.open(file_path, "r", "utf-8") as rfile:
                data = rfile.read()
            with codecs.open(file_path, "w", "utf-8") as wfile:
                for key, value in mappingData.items():
                    # 使用 re.sub() 进行查找和替换
                    newValue = re.sub(pattern, lambda x: x.group()[:-1] + '🎵;', value)
                    data = data.replace(key, newValue)
                wfile.write(data)
                print(fr'fileName: {fileName}')

        elif os.path.isdir(file_path):
            replace_x(file_path, mappingData)


# 替换🎵符为空字符串""
def replaceStr(folder_path):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for fileName in dirs:
        file_path = os.path.join(cwd, fileName)
        if os.path.isfile(file_path) and file_path.split('.')[-1] == "smali":
            with codecs.open(file_path, "r", "utf-8") as rfile:
                data = rfile.read()
            with codecs.open(file_path, "w", "utf-8") as wfile:
                data = data.replace("🎵", "")
                wfile.write(data)
        elif os.path.isdir(file_path):
            replaceStr(file_path)


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


def getOrderData(dataList, isMethod=False):
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
    if len(tempList) > 0 and isMethod:
        print(f"*********需要查看以下字段或方法是否被重复替换*********")
        print(tempList)
    for item in tempList:
        value = newMappingData[item]
        mappingData[item] = value
    return mappingData


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    mCurPath = os.getcwd()

    methodPath = f"{mCurPath}/scripts/findX/field_method.json"
    if isPlus:
        methodPath = f"{mCurPath}/scripts/findX/plus/method_plus.json"
    method_data = load_json_data(methodPath)
    method_data = getOrderData(method_data, isMethod=True)
    replace_x(from_dir, method_data)
    print("************LX相关属性和方法全部替换完成************")

    classPath = f"{mCurPath}/scripts/findX/class.json"
    if isPlus:
        classPath = f"{mCurPath}/scripts/findX/plus/class_plus.json"
    class_data = load_json_data(classPath)
    class_data = getOrderData(class_data)
    replace_x(from_dir, class_data)
    print("************LX相关的类替换完成************")
    replaceStr(from_dir)
    print("************程序执行结束************")
