import argparse
import json
import codecs
import os

baseVersion = "2.22.18.70"
newVersion = "2.22.22.80"


def load_json_data(file_path):
    with codecs.open(file_path, "r", "utf-8") as rfile:
        data = rfile.read()
    return json.loads(data)


def replace_x(folder_path, dataList):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for fileName in dirs:
        file_path = os.path.join(cwd, fileName)
        if os.path.isfile(file_path) and file_path.split('.')[-1] == "smali":
            with codecs.open(file_path, "r", "utf-8") as rfile:
                data = rfile.read()
            with codecs.open(file_path, "w", "utf-8") as wfile:
                replace_times = 0
                for item in dataList:
                    replace_times += data.count(item[baseVersion])
                    print(fr'fileName: {fileName} 替换次数：{replace_times}')

                    data = data.replace(item[baseVersion], item[newVersion])
                wfile.write(data)

        elif os.path.isdir(file_path):
            replace_x(file_path, dataList)


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
            replace_x(args.from_dir, method_data)
            print("************LX相关属性和方法全部替换完成************")
            break
        else:
            break

    while True:
        exit_flag = input('class2.json对应关系全部替换完成？yes or no \n')
        if exit_flag == 'yes':
            class_data = load_json_data(f"{mCurPath}/scripts/findX/class2.json")
            replace_x(args.from_dir, class_data)
            print("************LX相关的类替换完成************")
            break
        else:
            break
