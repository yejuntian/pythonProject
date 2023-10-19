import argparse
import glob
import os.path
import json
import codecs
import re
import xml.etree.ElementTree as ET

# 用来保存没有发现集合
notFoundDict = {}
# 用来保存错误attr集合列表
attrDict = {}
# 需要特殊处理的类型
specialTypeList = ["dimen", "style"]
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
        setAllAttr(file_path, public_map)
    # R$styleable.smali value值
    # print(attrDict)
    for file_path in file_list:
        if os.path.basename(file_path) == "R$styleable.smali":
            replaceStyleable(file_path, public_map)
        else:
            write_data_2_file(file_path, public_map)
    save2File(notFoundDict, f"{os.getcwd()}/scripts/values/native_values/GBNeedToFind.json")


# 设置所有属性到attrDict
def setAllAttr(file_path, public_map):
    file_name = os.path.basename(file_path)
    file_type = file_name.split("$")[1].split(".")[0]
    attrList = public_map.get("attr")
    with open(file_path, encoding="utf-8", mode="r") as rf:
        lines = rf.readlines()
        for line in lines:
            if line.startswith(".field public static final"):
                attr_name = line.split(":")[0].split(" ")[-1]
                attr_value = line.split("=")[-1].strip()
                newId = attrList.get(attr_name)
                # 用来保存所有错误的attr属性
                if file_type == "attr" and newId is not None and newId != attr_value:
                    # print(f"attr_value = {attr_value} attr_name = {attr_name}")
                    attrDict[attr_value] = attr_name


def replaceStyleable(file_path, public_map):
    attrIdList = public_map["attr"]
    with codecs.open(file_path, "r", "utf-8") as rf:
        lines = rf.readlines()
    with codecs.open(file_path, "w", "utf-8") as wf:
        data = getReplaceResult(lines, attrIdList)
        wf.write(data)


def getReplaceResult(lines, attrIdList):
    regex = r"0x7f\w{6}"
    result = ""
    for index, line in enumerate(lines):
        matches = re.finditer(regex, line, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            attrValueId = match.group()
            attrName = attrDict.get(attrValueId)
            # if attrValueId == '0x7f0407ca':
            #     print("attrName = " + attrName)
            # print(f"attrValueId = {attrValueId} attrName = {attrName}")
            if attrName is not None and attrIdList.get(attrName) is not None:
                line = line.replace(attrValueId, attrIdList.get(attrName))
        result += line
    return result


def write_data_2_file(file_path, public_map):
    file_name = os.path.basename(file_path)
    file_type = file_name.split("$")[1].split(".")[0]
    data = ""
    with open(file_path, encoding="utf-8", mode="r") as rf:
        lines = rf.readlines()
        for line in lines:
            if line.startswith(".field public static"):
                attr_name = line.split(":")[0].split(" ")[-1]
                attr_value = line.split("=")[-1].strip()
                # print(f"file_type = {file_type} attr_name = {attr_name}")
                # 用来保存没有找到的属性到notFoundDict
                if notFoundDict.get(file_type) is None:
                    notFoundDict[file_type] = []
                if not attr_name in public_map[file_type]:
                    notFoundDict[file_type].append(attr_name)
                # 只有匹配到的才进行赋值
                if not public_map[file_type].get(attr_name) is None:
                    attr_id = public_map[file_type][attr_name]
                    preStr = ".field public static"
                    if line.startswith(".field public static final"):
                        preStr = ".field public static final"
                    data += f"{preStr} {attr_name}:I = {attr_id}\n"
                else:  # 否则保留之前的value数值
                    data += line
            else:
                data += line
    with open(file_path, encoding="utf-8", mode="w") as wf:
        wf.write(data)


def save2File(dataList, fpath):
    parentDir = os.path.dirname(fpath)
    if not os.path.exists(parentDir):
        os.makedirs(parentDir, exist_ok=True)
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
            if attr_type in specialTypeList and attr_name.__contains__("."):
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
