import argparse
import glob
import os.path
import xml.etree.ElementTree as ET

"""
    主要作用：替换sdk目录R$*.smali资源文件value值
"""


def merge_sdk(sdk_dir, public_dir):
    """
        sdk_dir:sdk目录
        public_dir：public.xml绝对路径
    """
    file_list = glob.glob(pathname=sdk_dir + "/**/R$*smali", recursive=True)
    if len(file_list) <= 0: return
    public_map = get_public_data(public_dir)

    for file_path in file_list:
        write_data_2_file(file_path, public_map)


def write_data_2_file(file_path, public_map):
    file_name = os.path.basename(file_path)
    file_type = file_name.split("$")[1].split(".")[0]
    if file_name != "R$styleable.smali":
        data = ""
        with open(file_path, encoding="utf-8", mode="r") as rf:
            lines = rf.readlines()
            for line in lines:
                if line.startswith(".field public static final"):
                    attr_name = line.split(":")[0].split(" ")[-1]
                    #print(f"file_type = {file_type} attr_name = {attr_name}")
                    attr_id = public_map[file_type][attr_name]
                    data += f".field public static final {attr_name}:I = {attr_id}\n"
                else:
                    data += line
        with open(file_path, encoding="utf-8", mode="w") as wf:
            wf.write(data)


def get_public_data(public_dir):
    parse = ET.parse(public_dir)
    root = parse.getroot()
    public_map = {}
    for child in root:
        attrib = child.attrib
        if "id" in attrib and "name" in attrib:
            attr_type = attrib["type"]
            attr_name = attrib["name"]
            attr_id = attrib["id"]
            if attr_name.__contains__("."):
                attr_name = attr_name.replace(".", "_")
                # print(f"attr_type = {attr_type} attr_name = {attrib['name']}")
            if attr_type not in public_map:
                public_map[attr_type] = {}
            public_map[attr_type][attr_name] = attr_id

    return public_map


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sdk_dir")
    parser.add_argument("public_dir")
    args = parser.parse_args()
    merge_sdk(args.sdk_dir, args.public_dir)
    print(f"程序执行结束，输出结果保存到：{args.sdk_dir}")
