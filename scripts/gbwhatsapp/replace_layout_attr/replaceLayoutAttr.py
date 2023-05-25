import codecs
import json
import os
import re

# 16进制正则表达式
regexStr = r"0x7f[0-9a-f]{6}"
# from_dir匹配xml资源属性
regexAttrStr = r'android:(\w+)="([^"]*)"'
# to_dir 所有匹配属性的集合
targetRegexAttrStr = r'android:="([^"]+)"'
# from_dir 所有layout xml文件属性集合
fromAttrDict = {}
# from_dir 所有layout xml文件属性总个数
from_dir_attrs_count = 0
# 写入to_dir 所有layout xml文件属性总个数
to_dir_attrs_count = 0
# 是否保存文件
isSaveFile = False

"""
    1.注意事项：
        from_dir:使用jadx导出WhatsApp基础版本的gradle项目路径
        to_dir:使用apktool反编译WhatsApp基础版本的项目路径
        eg:
        from_dir = "/Users/shareit/work/GBWorke/whatsapp_v2.23.10.76_java"
        to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.10.76"
    2.该脚本主要作用：
        复制from_dir所有layout目录下所有xml布局属性，匹配to_dir对应layout目录下对应xml文件，
        对符合android:id="XXX"这种格式进行矫正，最后矫正为android:XXX="XXX"正确格式的android xml布局属性。
"""


def replaceMatchLayoutAttrs(from_dir, to_dir):
    findAttrs(from_dir, fromAttrDict)
    if isSaveFile:
        save2File(fromAttrDict, mCurrentPath, "from_layout_attrs.json")
    transFolderWriteXmlAttrs(to_dir, fromAttrDict)
    print(f"程序执行结束，查找属性总个数为：{from_dir_attrs_count} 写入属性中个数为：{to_dir_attrs_count}")


# 遍历所有layout目录，并写入xml属性到对应文件中
def transFolderWriteXmlAttrs(from_dir, fromAttrsDict):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath) and fname.startswith("layout"):
            transFolderWriteXmlAttrs(fpath, fromAttrsDict)
        elif os.path.isfile(fpath):
            dirName = from_dir.split("/")[-1]
            folderAttrList = fromAttrsDict.get(dirName)
            writeLayoutXmlAttrs(fpath, fname, folderAttrList)


# 向to_dir/layout所在目录中写入xml属性
def writeLayoutXmlAttrs(fpath, fname, folderAttrList):
    # 查找符合regexStr正则规则的xml属性
    attrKey = fname.split(".")[0]
    if re.search(regexStr, fname):
        matches = re.finditer(regexStr, fname, re.MULTILINE)
        for match in matches:
            attrKey = match.group()
    else:
        attrKey = fname.split(".")[0]
    # 每个xml文件对应属性集合list
    fileAttrsList = folderAttrList.get(attrKey)
    if len(fileAttrsList) > 0:
        with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
            data = rf.read()
        with codecs.open(fpath, mode="w", encoding="utf-8") as wf:
            result = re.sub(r'android:="([^"]*)"', lambda match: replace_match(match, fileAttrsList), data)
            wf.write(result)


def replace_match(match, data_list):
    global to_dir_attrs_count
    to_dir_attrs_count += 1
    attribute_value = match.group(1)
    replacement = f'android:{data_list.pop(0)}="{attribute_value}"'
    return replacement


# 查找所有layout目录下xml符合正则规则的属性，保存到allAttrDict集合中
def findAttrs(from_dir, allAttrDict):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath) and fname.startswith("layout"):
            parentDirName = fpath.split("/")[-1]
            allAttrDict[parentDirName] = {}
            findAttrs(fpath, allAttrDict)
        elif os.path.isfile(fpath):
            dirName = from_dir.split("/")[-1]
            folderAttrDict = allAttrDict.get(dirName)
            setFileAttrDict(fpath, fname, folderAttrDict)


# 获取layout xml所有标签属性,并保持到fileAttrDict字典中
def setFileAttrDict(fpath, fname, fileAttrDict):
    global from_dir_attrs_count
    # 查找符合regexStr正则规则的xml属性
    if re.search(regexStr, fname):
        matches = re.finditer(regexStr, fname, re.MULTILINE)
        for match in matches:
            tempAttrList = []
            with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
                matches = re.finditer(regexAttrStr, rf.read(), re.MULTILINE)
                for fMatch in matches:
                    tempAttrList.append(fMatch.group(1))
            fileAttrDict[match.group()] = tempAttrList
            from_dir_attrs_count += len(tempAttrList)
    else:  # 除了regexStr正则之外其他xml属性
        tempAttrList = []
        with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
            matches = re.finditer(regexAttrStr, rf.read(), re.MULTILINE)
            for fMatch in matches:
                tempAttrList.append(fMatch.group(1))
        fileAttrDict[fname.split(".")[0]] = tempAttrList
        from_dir_attrs_count += len(tempAttrList)
    return fileAttrDict


def save2File(dataList, folder_path, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    from_dir = "/Users/shareit/work/GBWorke/whatsapp_d"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/whatsapp_1"
    replaceMatchLayoutAttrs(f"{from_dir}/app/src/main/res", f"{to_dir}/res")
