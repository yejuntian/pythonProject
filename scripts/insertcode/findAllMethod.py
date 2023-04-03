import os
import codecs
import re
import json
import glob

# 只匹配下面的文件类型
extends = ["smali"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml',
             'res', 'smali_classes5', 'smali_classes6', 'smali_classes7', 'AndroidManifest.xml']
# whatsapp 所有方法
allMethod = []
allMethodRegex = r"L.*\w+;->\w+\(.*\).*"
# 需要插入的所有方法
folderList = ['smali_classes5', 'smali_classes6']
insertMethod = []
insertMethodRegex = r"\.method .*?(\w+\(.*\).*)"
# 项目绝对路径
projectPath = ""


def findAllMethod(from_dir):
    transformFolder(from_dir)
    transformNewFolder(from_dir)
    saveFile()


def saveFile():
    methodList = []
    for method in insertMethod:
        if method in allMethod:
            methodList.append(method)
    save_2_file(f"{os.getcwd()}/method.json", methodList)


# 保存到文件中
def save_2_file(fpath, dataList):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w+", "utf-8") as wfile:
        wfile.write(jsonStr)
    print(f"结果保存到：{fpath}")


# 遍历folderList列表中的文件夹列表，获取所有的method
def transformNewFolder(from_dir):
    depMethodList = []
    for folder in folderList:
        fileList = glob.glob(f"{from_dir}/{folder}/**/*.smali", recursive=True)
        for fpath in fileList:
            print(fpath)
            relativePath = fpath[len(projectPath + folder) + 2:]
            relativePath = relativePath[0:relativePath.rindex("/")]
            fname = os.path.basename(fpath)
            with codecs.open(fpath, "r", "utf-8") as rf:
                matches = re.finditer(insertMethodRegex, rf.read(), re.MULTILINE)
                for matchNum, match in enumerate(matches, start=1):
                    method = match.group(1)
                    name = fname.split(".")[0]
                    newMethod = f"L{relativePath + '/' + name};->{method}"
                    # print(newMethod)
                    # 特殊处理
                    if newMethod.__contains__("Lcom/silence"):
                        newMethod = newMethod.replace("Lcom/silence", "Lcow/silence")
                    if not newMethod in insertMethod:
                        insertMethod.append(newMethod)
                        if newMethod.__contains__("Lcom/gbwhatsapp/yo/dep;"):
                            depMethodList.append(newMethod)
    # 因为yo.smali继承dep.smali,需要特殊处理
    for method in depMethodList:
        newMethod = method.replace("Lcom/gbwhatsapp/yo/dep;", "Lcom/gbwhatsapp/yo/yo;")
        if not newMethod in insertMethod:
            insertMethod.append(newMethod)


# 遍历smali文件获取所有的method
def transformFolder(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        if fname not in blacklist:
            fpath = os.path.join(from_dir, fname)
            if os.path.isdir(fpath):
                transformFolder(fpath)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends:
                    print(fpath)
                    with codecs.open(fpath, "r", "utf-8") as rf:
                        matchRes(allMethodRegex, rf.read(), 0, allMethod)


def matchRes(regex, content, groupIndex, dataList):
    matches = re.finditer(regex, content, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        method = match.group(groupIndex)
        if not method in dataList and not "Lcom/google/" in method:
            dataList.append(method)


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.2.76"
    projectPath = from_dir
    findAllMethod(from_dir)
