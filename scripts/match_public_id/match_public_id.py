import argparse
import codecs
import json
import os
import re
import xml.etree.ElementTree as ET

# 只匹配下面的文件类型
extends = ["smali"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 匹配from_dir和to_dir项目，public.xml属性ID的对应关系
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


def matchPublicId(from_dir, to_dir, targetFolder):
    # 获取public.xml的关系
    from_public_path = f"{from_dir}/res/values/public.xml"
    to_public_path = f"{to_dir}/res/values/public.xml"
    fromMappingValues = getMappingValues(from_public_path, {})
    toMappingValues = getMappingValues(to_public_path, {})
    matchValues(fromMappingValues, toMappingValues, matchId_dict)
    # 替换掉所有匹配正则的属性ID值
    transFolderIds(targetFolder, matchId_dict, allNotFindId, fromMappingValues, toMappingValues)
    if len(allNotFindId) > 0:
        save2File(allNotFindId, "NotFind.json")
    print(f"执行程序结束，结果保存在:{targetFolder}")


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
        if not toId is None:
            matchId_dict[fromId] = toId
    # print(matchId_dict)


def transFolderIds(targetFolder, matchId_dict, allNotFindId, fromMappingValues, toMappingValues):
    if os.path.isdir(targetFolder):
        listdir = os.listdir(targetFolder)
        for fname in listdir:
            fpath = os.path.join(targetFolder, fname)
            if fname not in blacklist:
                if os.path.isdir(fpath):
                    transFolderIds(fpath, matchId_dict, allNotFindId, fromMappingValues, toMappingValues)
                elif os.path.isfile(fpath):
                    if fname.split(".")[-1] in extends:
                        print(fpath)
                        startReplaceFile(fpath, toMappingValues, fromMappingValues)
    else:
        if targetFolder.split(".")[-1] in extends:
            startReplaceFile(targetFolder, toMappingValues, fromMappingValues)


# 替换
def startReplaceFile(fpath, toMappingValues, fromMappingValues):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
    with codecs.open(fpath, "w", "utf-8") as wf:
        idList = set()
        # 匹配id
        matches = re.finditer(regexStr, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            matchId = match.group()
            idList.add(matchId)
        # 替换id
        replace_times = 0
        for attrId in idList:
            searchId = matchId_dict.get(attrId)
            if not searchId is None:
                replace_times += data.count(attrId)
                # print(f"attrId = {attrId} searchId = {searchId}")
                data = data.replace(attrId, searchId)
            else:
                if searchId in toMappingValues.values() or searchId in fromMappingValues:
                    allNotFindId[attrId] = fpath
        print(r'替换次数：', replace_times)
        wf.write(data)


def save2File(dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fileName, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，没有找到的ID保存在:{os.path.join(os.getcwd(), fileName)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    targetFolder = args.to_dir
    to_dir = targetFolder[0:(targetFolder.index("smali_")) - 1]
    matchPublicId(from_dir, to_dir, targetFolder)

    # from_dir = "/Users/shareit/work/shareit/whatsapp-decode-v212116000/DecodeCode/WhatsApp_v2.22.7.74"
    # to_dir = "/Users/shareit/work/shareit/whatsapp-decode-v212116000/DecodeCode/WhatsApp_v2.22.22.80"
    # targetFolder = "/Users/shareit/work/shareit/whatsapp-decode-v212116000/DecodeCode/WhatsApp_v2.22.22.80/smali_classes4/zoo/update/NewVersionDialog.smali"
    # matchPublicId(from_dir, to_dir, targetFolder)
