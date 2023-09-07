import argparse
import codecs
import os
import re
import shutil
import lxml.etree as ET

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', "res",
             'original', 'AndroidManifest.xml', 'apktool.yml']
# android命名空间约束
android_scheme = "http://schemas.android.com/apk/res/android"
strDict = {"market://details?id=com.gbwhatsapp.w4b&utm_source="
           : "market://details?id=com.whatsapp.w4b&utm_source=",
           "com.gbwhatsapp.sticker.READ": "com.whatsapp.sticker.READ"}
pattern = re.compile(r'smali_classes(\d+)')

"""
    主要作用：
        1.删除from_dir无用目录，并校正字符串
        2.调用moveFiles方法copy文件到目标目录
"""


# 替换AndroidManifest.xml特定字符
def replaceManifest(fpath):
    ET.register_namespace('android', android_scheme)
    parser = ET.parse(fpath)
    root = parser.getroot()
    rootAttrib = root.attrib
    nameSpace = "{" + android_scheme + "}"
    rootAttrib[nameSpace + "compileSdkVersion"] = "23"
    rootAttrib[nameSpace + "compileSdkVersionCodename"] = "6.0-2438415"
    rootAttrib["platformBuildVersionCode"] = "33"
    rootAttrib["platformBuildVersionName"] = "13"

    for child in root:
        childAttrib = child.attrib
        child_tag = child.tag
        if child_tag == "queries":
            queries(child, nameSpace)
        elif child_tag == "uses-permission":
            permissionName = childAttrib.get(nameSpace + "name")
            if not permissionName is None and permissionName == "com.gbwhatsapp.sticker.READ":
                childAttrib[nameSpace + "name"] = "com.whatsapp.sticker.READ"
        elif child_tag == "application":
            for subChild in child:
                subChildAttrib = subChild.attrib
                subChildAttrName = subChildAttrib.get(nameSpace + "name")
                if subChild.tag == "activity" and not subChildAttrName is None and subChildAttrName.__contains__(
                        "AddThirdPartyStickerPackActivity"):
                    for intentChild in subChild:
                        for subChild in intentChild:
                            if subChild.tag == "action":
                                actionName = subChild.attrib.get(nameSpace + "name")
                                if not actionName is None:
                                    subChild.attrib[nameSpace + "name"] = actionName.replace("gbwhatsapp", "whatsapp")

    data_str = ET.tostring(root, encoding="utf-8").decode('utf-8').replace(' />', '/>')
    xml_data = f'<?xml version="1.0" encoding="utf-8" standalone="no"?>{data_str}'
    write_2_file(fpath, xml_data)


def queries(root, nameSpace):
    for child in root:
        authorities = child.attrib.get(nameSpace + "authorities")
        if child.tag == "provider" and not authorities is None and authorities.__contains__(".car.app.connection"):
            child.attrib[nameSpace + "name"] = "androidy.car.app.connection"


def write_2_file(file_path, data_str):
    try:
        with codecs.open(file_path, mode='w+', encoding="utf-8") as f:
            f.write(data_str)
    except Exception as result:
        print(f"写入{file_path}异常: {result}")


# 替换apktool.yml特定字符
def replaceApktool(fpath):
    with codecs.open(fpath, "r", "utf-8") as rf:
        lines = rf.readlines()
    with codecs.open(fpath, "w", "utf-8") as wf:
        result = ""
        global pos
        size = len(lines)
        for index in range(size):
            line = lines[index]
            if line.__contains__("- resources.arsc"):
                newLine = line + "- png\n- ogg\n- m4a\n- mp4\n"
                result += newLine
            elif line.__contains__("- png") or line.__contains__("- ogg") \
                    or line.__contains__("- m4a") or line.__contains__("- mp4"):
                continue
            elif line.__contains__("targetSdkVersion"):
                newLine = "  targetSdkVersion: '33'\n"
                result += newLine
            elif line.__contains__("unknownFiles:"):
                newLine = "unknownFiles: {}\n"
                result += newLine
                pos = index
                break
            else:
                result += line
        # 找到usesFramework:位置
        for index in range(pos, len(lines)):
            line = lines[index]
            if line.__contains__("usesFramework:"):
                pos = index
                break
        for index in range(pos, len(lines)):
            line = lines[index]
            result += line
        wf.write(result)


# 删除unknown文件夹(包括子文件),并替换特定字符串
def transFolderReplaceStr(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if not fname in blacklist:
            if os.path.isdir(fpath):
                if fname == "unknown":
                    shutil.rmtree(fpath, ignore_errors=True)
                else:
                    transFolderReplaceStr(fpath)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] == "smali":
                    with codecs.open(fpath, "r", "utf-8") as rf:
                        data = rf.read()
                    with codecs.open(fpath, "w", "utf-8") as wf:
                        for key, value in strDict.items():
                            data = data.replace(key, value)
                        wf.write(data)


# copy 文件到指定目录
def moveFiles(folderPath, mCurrentPath, folderName):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath, exist_ok=True)
    currentFolderPath = f"{mCurrentPath}/scripts/gbwhatsapp/{folderName}"
    transFolderCopyFile(currentFolderPath, folderPath)


# 遍历目录，层级copy文件到指定文件夹中
def transFolderCopyFile(from_dir, targetFolderPath):
    listDir = os.listdir(from_dir)
    for fname in listDir:
        fpath = os.path.join(from_dir, fname)
        tpath = os.path.join(targetFolderPath, fname)
        # print(f"fpath = {fpath} tpath = {tpath}")
        if os.path.isdir(fpath):
            # 创建目标文件夹
            if not os.path.exists(tpath):
                os.makedirs(tpath, exist_ok=True)
            transFolderCopyFile(fpath, tpath)
        elif os.path.isfile(fpath):
            if not os.path.exists(tpath):
                shutil.copy(fpath, tpath)


# 创建新目录并copy文件到新创建的目录中
def createNewFolderAndCopyFile(from_dir, mCurrentPath):
    folder_list = os.listdir(from_dir)
    matching_folders = [folder for folder in folder_list if pattern.match(folder)]
    if matching_folders is not None and len(matching_folders) > 0:
        numbers = [int(pattern.match(folder).group(1)) for folder in matching_folders]
        # 构造需要加1的目标文件夹名称
        targetFolderName = 'smali_classes' + str(max(numbers) + 1)
        moveFiles(f"{from_dir}/{targetFolderName}/gbwhatsapp/yo", mCurrentPath, "yo")
        moveFiles(f"{from_dir}/{targetFolderName}/com", mCurrentPath, "com")


# 删除项目空文件夹
def deleteProjectEmptyFolder(from_dir):
    for root, dirs, files in os.walk(from_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # 如果文件夹为空
                os.rmdir(dir_path)  # 删除空文件夹


def other(from_dir, mCurrentPath):
    replaceManifest(f"{from_dir}/AndroidManifest.xml")
    replaceApktool(f"{from_dir}/apktool.yml")
    transFolderReplaceStr(from_dir)
    createNewFolderAndCopyFile(from_dir, mCurrentPath)
    deleteProjectEmptyFolder(from_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    other(from_dir, os.getcwd())
