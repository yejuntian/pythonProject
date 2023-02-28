import codecs
import json
import argparse

baseVersion = "2.22.22.80"
newVersion = "2.23.2.76"
method_data = []

"""
    组合field2.json、method2.json中类的对应关系，
    替换class2.json中对应版本的value值
"""


# 保存数据
def save_2_file(data, filePath):
    jsonStr = json.dumps(data, ensure_ascii=False, indent=2)
    with open(filePath, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{filePath}")


# 加载数据
def load_json_data(file_path):
    with codecs.open(file_path, "r", "utf-8") as rfile:
        data = rfile.read()
    return json.loads(data)


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


def packageData(from_dir):
    # 合并method数据
    method_data = load_json_data(f"{from_dir}/method2.json")
    fMethodPath = f"{from_dir}/method.json"
    method_data = mergeData(load_json_data(fMethodPath), method_data)
    save_2_file(method_data, fMethodPath)
    # 合并field数据
    field_data = load_json_data(f"{from_dir}/field2.json")
    fFieldPath = f"{from_dir}/field.json"
    field_data = mergeData(load_json_data(fFieldPath), field_data)
    save_2_file(field_data, fFieldPath)
    # 合并method数据
    class_data = load_json_data(f"{from_dir}/class2.json")
    fClassPath = f"{from_dir}/class.json"
    class_data = mergeData(load_json_data(fClassPath), class_data)
    save_2_file(class_data, fClassPath)


def mergeData(data, allData):
    for str in data:
        oldData = str[baseVersion]
        newData = str[newVersion]
        if newData == "":
            for item in allData:
                if oldData == item[baseVersion]:
                    str[newVersion] = item[newVersion]
                    continue
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir

    # from_dir = " /Users/shareit/work/pythonProject/scripts/findX"
    packageData(from_dir)
