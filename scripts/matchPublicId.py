import codecs
import json
import os
import xml.etree.ElementTree as ET

matchId_dict = {}
# 添加所有没有匹配的ID
allNotFindId = {}
# 16进制正则表达式
regexStr = r"0x7f[0-9a-f]{6}"

"""
    主要作用：反编译smali代码中,我们新增的代码使用findViewById(I)形式查找的ID值，替换为目标项目public.xml对应的属性ID值
    from_dir：参考项目地址
    to_dir：目标项目地址
    targetFolder：要替换smali代码中ID值的文件夹或文件地址
"""


def matchPublicId(from_dir, to_dir):
    # 获取public.xml的关系
    from_public_path = f"{from_dir}/res/values/public.xml"
    to_public_path = f"{to_dir}/res/values/public.xml"
    fromMappingValues = getMappingValues(from_public_path, {})
    toMappingValues = getMappingValues(to_public_path, {})
    matchValues(fromMappingValues, toMappingValues, matchId_dict)
    save2File(matchId_dict, "matchPublicId.json")


# 获取public资源ID和属性name、type的映射关系
def getMappingValues(fpath, mappingValues):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        attrId = attrib.get("id")
        if attrName is None or attrType is None or attrId is None:
            continue
        mappingValues[f"{attrType.strip()}#{attrName.strip()}"] = attrId
    return mappingValues


# 匹配ID对应关系
def matchValues(fromMappingValues, toMappingValues, matchId_dict):
    for fromName, fromId in fromMappingValues.items():
        toId = toMappingValues.get(fromName)
        if toId is not None:
            matchId_dict[fromId] = toId
    # print(matchId_dict)


def save2File(dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fileName, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，没有找到的ID保存在:{os.path.join(os.getcwd(), fileName)}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.20.76/DecodeCode/Whatsapp_v2.23.20.76"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.25.76/DecodeCode/Whatsapp_v2.23.25.76"
    matchPublicId(from_dir, to_dir)
