import argparse
import glob
import os.path
import json
import codecs
import xml.etree.ElementTree as ET

# 用来保存没有发现集合
notFoundDict = {}
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
    save2File(notFoundDict, f"{os.getcwd()}/scripts/values/native_values/GBNeedToFind.json")


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
                    # print(f"file_type = {file_type} attr_name = {attr_name}")
                    # 用来保存没有找到的属性到notFoundDict
                    if notFoundDict.get(file_type) is None:
                        notFoundDict[file_type] = []
                    if not attr_name in public_map[file_type]:
                        notFoundDict[file_type].append(attr_name)
                    # 只有匹配到的才进行赋值
                    if not public_map[file_type].get(attr_name) is None:
                        attr_id = public_map[file_type][attr_name]
                        data += f".field public static final {attr_name}:I = {attr_id}\n"
                    else:  # 否则保留之前的value数值
                        data += line
                else:
                    data += line
        with open(file_path, encoding="utf-8", mode="w") as wf:
            wf.write(data)


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


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
    args = parser.parse_args()
    sdkDir = args.sdk_dir
    projectFolder = sdkDir[0:(sdkDir.index("smali_")) - 1]
    merge_sdk(sdkDir, f"{projectFolder}/res/values/public.xml")
    print(f"程序执行结束，输出结果保存到：{sdkDir}")
