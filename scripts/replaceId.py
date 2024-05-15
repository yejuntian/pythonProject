import codecs
import json
import os
import re
import lxml.etree as ET

# 定义正则表达式和替换映射
# (?<![0-9a-f]) :确保匹配的部分不会超过八位数
regex_str = r"0x7f[0-9a-f]{6}(?![0-9a-f])"

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib', 'META-INF',
             'original', 'res', 'smali', 'smali_classes2', 'smali_classes3',
             'smali_classes4', 'smali_classes5', 'smali_classes6',
             'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["smali"]
# 源项目public.xml字典
from_publicDic = {}
# 源项目public.xml id集合
from_publicIds = []
# 用来保存没有找到的属性集合
notFoundDic = {}
# 用来存放没有找打的id
allNotFindId = set()
# 用来存放颜色值或switch case语句的常量值
constList = set()
# 排除的资源id集合
excludeIds = ['0x7fffffff', '0x7fc00000', '0x7f7fffff', '0x7fff0000',
              '0x7feafd65']

"""
    主要作用：反编译smali代码中,我们新增的代码使用findViewById(I)形式查找的ID值，替换为目标项目public.xml对应的属性ID值
    from_dir：参考项目地址
    to_dir：目标项目地址
"""


def replace_strings_in_smali_file(file_path, replacement_map):
    with open(file_path, 'r', encoding='utf-8') as file:
        smali_content = file.read()

    # 使用正则表达式查找字符串
    matches = re.findall(regex_str, smali_content)

    # 根据映射替换字符串
    for fromPublicId in matches:
        if fromPublicId in replacement_map:
            replacement_value = replacement_map[fromPublicId]
            replaced_value = replacement_value[:4] + "🎵" + replacement_value[4:]
            smali_content = smali_content.replace(fromPublicId, replaced_value)
        else:
            # 用来保存没有找到的属性集合
            attrList = from_publicDic.get(fromPublicId)
            if attrList is not None:
                attrType = attrList.split("#")[0]
                attrName = attrList.split("#")[1]
                if notFoundDic.get(attrType) is None:
                    notFoundDic[attrType] = []
                if attrName not in notFoundDic.get(attrType):
                    notFoundDic[attrType].append(attrName)
            else:
                # 证明该id是被注册public.xml的
                if fromPublicId in from_publicIds:
                    allNotFindId.add(fromPublicId)
                else:
                    if fromPublicId not in excludeIds:
                        constList.add(fromPublicId)

    # 将替换后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(smali_content)


def parsePublicXml(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrType = attrib.get("type")
        attrName = attrib.get("name")
        attrId = attrib.get("id")
        if attrType is None or attrName is None or attrId is None:
            continue
        from_publicDic[attrId] = f"{attrType}#{attrName}"
        from_publicIds.append(attrId)


def replaceId(folder_path, mappingData):
    if os.path.isdir(folder_path):
        dirs = os.listdir(folder_path)
        for fileName in dirs:
            file_path = os.path.join(folder_path, fileName)
            if os.path.isfile(file_path) and file_path.split('.')[-1] in extends:
                replace_strings_in_smali_file(file_path, mappingData)
            elif os.path.isdir(file_path) and fileName not in blacklist:
                replaceId(file_path, mappingData)
    else:
        replace_strings_in_smali_file(folder_path, mappingData)


# 替换文件🎵符为空字符串""
def replaceFileStr(fpath):
    with codecs.open(fpath, "r", "utf-8") as rfile:
        data = rfile.read()
    with codecs.open(fpath, "w", "utf-8") as wfile:
        data = data.replace("🎵", "")
        wfile.write(data)


# 遍历目录，替换🎵符为空字符串""
def replaceStr(folder_path):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for fileName in dirs:
        file_path = os.path.join(cwd, fileName)
        if os.path.isfile(file_path) and file_path.split('.')[-1] == "smali":
            replaceFileStr(file_path)
        elif os.path.isdir(file_path):
            replaceStr(file_path)


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"文件保存在:{fpath}")


# 注册到public.xml
def insertPublic(fpath, type, insetNameList):
    to_parser = ET.parse(fpath)
    to_root = to_parser.getroot()
    maxChild = None
    maxId = 0
    for child in to_root:
        attr = child.attrib
        attrType = attr.get("type")
        attrId = attr.get("id")
        if attrType is not None and attrType == type:
            attrId = int(attrId, 16)
            if attrId >= maxId:
                maxId = attrId
                maxChild = child

    pos = to_root.index(maxChild)

    for itemName in insetNameList:
        maxId += 1
        pos += 1

        element = ET.SubElement(to_root, "public")
        element.set("type", type)
        element.set("name", itemName)
        element.set("id", str(hex(maxId)))
        to_root.insert(pos, element)

    # 写入到public.xml文件中
    with codecs.open(fpath, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for child in to_root:
            attrType = child.attrib.get("type")
            attrName = child.attrib.get("name")
            attrId = child.attrib.get("id")
            wf.write(f'    <public type="{attrType}" name="{attrName}" id="{attrId}" />\n')
        wf.write('</resources>')


def replace_strings_in_directory(fromPath, toPath, mappingPath):
    with open(mappingPath, "r") as f:
        replacement_map = json.loads(f.read())
    parsePublicXml(f"{fromPath}/res/values/public.xml")
    replaceId(toPath, replacement_map)
    if len(notFoundDic) > 0:
        print("执行程序结束，没有找到的资源保存到：")
        fpath = "/Users/shareit/work/pythonProject/scripts/values/native_values/GBNeedToFind.json"
        save2File(notFoundDic, fpath)
        # 注册public.xml
        # idsNameList = notFoundDic.get("id")
        # if idsNameList is not None and len(idsNameList) > 0:
        #     toPublicXmlPath = toPath[0:(toPath.index("smali_")) - 1]
        #     insertPublic(f"{toPublicXmlPath}/res/values/public.xml", "id", idsNameList)
    # 删除标记
    if os.path.isdir(toPath):
        replaceStr(toPath)
    else:
        replaceFileStr(toPath)
    print("****************执行结果结束****************\n")
    # 打印替换结果
    printResult()


def printResult():
    # 打印没有查到的ID
    if len(allNotFindId) > 0:
        print(f"****************没有找到的资源ID如下：****************\n")
        print(allNotFindId)
    if len(constList) > 0:
        print(f"****************smali文件使用的常量值如下：****************\n")
        print(constList)


if __name__ == "__main__":
    from_path = "/Users/shareit/work/shareit/wagb-shell/app-gb-release"
    to_path = "/Users/shareit/work/shareit/gbwhatsapp_2.24.3.81/DecodeCode/Whatsapp_v2.24.3.81/smali_classes9/androidx"
    mappingPath = "/Users/shareit/work/pythonProject/scripts/matchPublicId.json"
    # 执行替换操作
    replace_strings_in_directory(from_path, to_path, mappingPath)
    print("--------程序执行结束------------")
