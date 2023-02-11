import argparse
import codecs
import json
import os

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin', 'lib', 'META-INF',
             'original', 'res', 'smali', 'smali_classes2', 'smali_classes3',
             'smali_classes4', 'smali_classes7', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["smali"]

baseVersion = "2.22.22.80"
newVersion = "2.23.2.76"


def load_json_data(file_path):
    with codecs.open(file_path, "r", "utf-8") as rfile:
        data = rfile.read()
    return json.loads(data)


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


def replace_x(folder_path, mappingData):
    dirs = os.listdir(folder_path)
    for fileName in dirs:
        file_path = os.path.join(folder_path, fileName)
        if os.path.isfile(file_path) and file_path.split('.')[-1] in extends:
            with codecs.open(file_path, "r", "utf-8") as rfile:
                data = rfile.read()
            with codecs.open(file_path, "w", "utf-8") as wfile:
                replace_times = 0
                for key, value in mappingData.items():
                    replace_times += data.count(key)

                    data = data.replace(key, value)
                wfile.write(data)
                print(fr'fileName: {fileName} 替换次数：{replace_times}')

        elif os.path.isdir(file_path) and fileName not in blacklist:
            replace_x(file_path, mappingData)


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    mCurPath = os.getcwd()

    while True:
        exit_flag = input('method2.json、field2.json对应关系全部替换完成？yes or no \n')
        if exit_flag == 'yes':
            method_data = load_json_data(f"{mCurPath}/scripts/findX/method2.json")
            filed_data = load_json_data(f"{mCurPath}/scripts/findX/field2.json")
            method_data.extend(filed_data)
            method_data = getOrderData(method_data)
            replace_x(args.from_dir, method_data)
            print("************LX相关属性和方法全部替换完成************")
            break
        else:
            break

    while True:
        exit_flag = input('class2.json对应关系全部替换完成？yes or no \n')
        if exit_flag == 'yes':
            class_data = load_json_data(f"{mCurPath}/scripts/findX/class2.json")
            class_data = getOrderData(class_data)
            replace_x(args.from_dir, class_data)
            print("************LX相关的类替换完成************")
            break
        else:
            break