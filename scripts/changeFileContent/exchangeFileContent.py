import argparse
import codecs
import json
import os

"""
    主要作用：将提供的文件列表根据对应关系，交换文件内容
"""


def group_files(file_list):
    # 按照文件名（忽略大小写）进行分组
    groups = {}

    for file in file_list:
        # 提取基础文件名（忽略大小写），去掉扩展名
        base_name = file.split('.')[0].lower()
        if base_name not in groups:
            groups[base_name] = []
        groups[base_name].append(file)

    return groups


def swap_file_contents(mapping, base_path):
    # 遍历映射关系并执行内容替换
    for key, value in mapping.items():
        # 根据 key 在 base_path 查找文件
        source_files = find_in_smali(base_path, key.strip())
        target_files = find_in_smali(base_path, value.strip())

        if len(source_files) == 1 and len(target_files) == 1:
            # 确保两个文件都存在并读取内容
            with open(source_files[0], 'r') as src, open(target_files[0], 'r') as tgt:
                source_content = src.read()
                target_content = tgt.read()

            # 交换内容
            with open(source_files[0], 'w') as src, open(target_files[0], 'w') as tgt:
                src.write(target_content)
                tgt.write(source_content)
        else:
            print(f"未找到文件: {key} 或 {value}")


def find_in_smali(base_path, file_name):
    matches = []

    # 遍历 base_path 下的所有目录逐层递归
    for dir_name in os.listdir(base_path):
        dir_path = os.path.join(base_path, dir_name)

        # 检查是否是以 "smali" 开头的目录
        if os.path.isdir(dir_path) and dir_name.startswith("smali"):
            # 检查 smali*/X 目录是否存在
            x_path = os.path.join(dir_path, "X")
            if os.path.isdir(x_path):
                # 查找 smali*/X 下是否存在目标文件
                if file_name in os.listdir(x_path):
                    matches.append(os.path.join(x_path, file_name))

    return matches


# 加载映射关系
def loadData(fpath):
    tempDict = {}
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        data = json.loads(rf.read())
        for key, value in data.items():
            if str and value:
                tempDict[key] = value
    return tempDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/instaldiff_278.0.0.21.117-367809465/DecodeCode/instagram_278.0.0.21.117"
    mapping = loadData(f"{os.getcwd()}/scripts/changeFileContent/fileMapping.json")
    # 根据映射关系替换文件内容
    swap_file_contents(mapping, from_dir)
    print("***********程序执行结束****************")
