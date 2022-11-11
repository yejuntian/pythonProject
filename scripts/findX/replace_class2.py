import argparse
import codecs
import json

baseVersion = "2.22.10.73"
newVersion = "2.22.18.70"
method_data = []

"""
    组合field2.json、method2.json中类的对应关系，
    替换class2.json中对应版本的value值
"""


def replace_class2(from_dir):
    filePath = f"{from_dir}/class2.json"
    class_data = load_json_data(filePath)
    class_data = merge_data(class_data, method_data)
    jsonStr = json.dumps(class_data, ensure_ascii=False, indent=2)
    with open(filePath, "w+") as wf:
        wf.write(jsonStr)


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir

    method_data = load_json_data(f"{from_dir}/method2.json")
    filed_data = load_json_data(f"{from_dir}/field2.json")
    method_data.extend(filed_data)
    replace_class2(from_dir)
    print(f"程序执行结束，结果保存在{from_dir}/class2.json")
