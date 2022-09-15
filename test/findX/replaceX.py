import argparse
import json
import codecs
import os


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
        if os.path.isfile(file_path):
            with codecs.open(file_path, "r", "utf-8") as rfile:
                data = rfile.read()
            with codecs.open(file_path, "w", "utf-8") as wfile:
                replace_times = 0
                for item in dataList:
                    replace_times += data.count(item["2.22.10.73"])
                    print(fr'fileName: {fileName} 替换次数：{replace_times}')

                    data = data.replace(item["2.22.10.73"], item["2.22.18.70"])
                wfile.write(data)

        elif os.path.isdir(file_path):
            replace_x(file_path, dataList)


# 组装数据
def merge_data(class_data, method_data):
    for class_item in class_data:
        old_class = class_item["2.22.10.73"]
        for item in method_data:
            item_class = item["2.22.10.73"]
            item_class2 = item["2.22.18.70"]
            if old_class == item_class.split("->")[0]:
                class_item["2.22.18.70"] = item_class2.split("->")[0]
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
            method_data = load_json_data(f"{mCurPath}/test/findX/method2.json")
            filed_data = load_json_data(f"{mCurPath}/test/findX/field2.json")
            method_data.extend(filed_data)
            replace_x(args.from_dir, method_data)
            print("************LX相关属性和方法全部替换完成************")

            class_data = load_json_data(f"{mCurPath}/test/findX/class.json")
            class_data = merge_data(class_data, method_data)
            jsonStr = json.dumps(class_data, ensure_ascii=False, indent=4)
            with open(f"{mCurPath}/test/findX/class2.json", "w+") as wf:
                wf.write(jsonStr)
            break
        else:
            break

    while True:
        exit_flag = input('class2.json对应关系全部替换完成？yes or no \n')
        if exit_flag == 'yes':
            class_data = load_json_data(f"{mCurPath}/test/findX/class2.json")
            replace_x(args.from_dir, class_data)
            print("************LX相关的类替换完成************")
            break
        else:
            break
