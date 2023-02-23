import os
import codecs
import re
import glob
import xml.etree.ElementTree as ET
import json

# 只匹配下面的文件类型
extends = ["smali"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin', 'lib', 'META-INF',
             'original', 'res', 'smali', 'smali_classes2', 'smali_classes3',
             'smali_classes4', 'AndroidManifest.xml', 'apktool.yml']
regex = r"\"(.*?)\""
allStringDict = {}


def findStr(from_dir):
    mappingData = getPublic(f"{from_dir}/res/values/public.xml")
    transFolder(from_dir, mappingData)
    # getAllSmaliAttrName(from_dir, mappingData)
    save2File(allStringDict, f"json_data/allString.json")


# 替换R$*.smali 属性名
def getAllSmaliAttrName(from_dir, mappingData):
    file_list = glob.glob(pathname=from_dir + "/**/R$*smali", recursive=True)
    if len(file_list) <= 0: return
    for fpath in file_list:
        replaceSmaliFile(fpath, mappingData)


def replaceSmaliFile(fpath, mappingData):
    fileName = os.path.basename(fpath)
    if fileName != "R$styleable.smali":
        data = ""
        with open(fpath, encoding="utf-8", mode="r") as rf:
            lines = rf.readlines()
            for line in lines:
                if line.startswith(".field public static final"):
                    attrId = line.split(" = ")[-1].replace("\n", "")
                    # print(f"fpath = {fpath} attrId = {attrId}")
                    attrName = mappingData.get(attrId)
                    if not attrName is None:
                        data += f".field public static final {attrName}:I = {attrId}\n"



def getPublic(fpath):
    mappingData = {}
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        type = attrib.get("type")
        name = attrib.get("name")
        id = attrib.get("id")
        if id is None or type is None or name is None:
            continue
        if mappingData.get(type) is None:
            mappingData[type] = []
        mappingData[type].append(name)
    return mappingData


def transFolder(from_dir, mappingData):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if not fname in blacklist:
            if os.path.isdir(fpath):
                transFolder(fpath, mappingData)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends:
                    print(fpath)
                    with codecs.open(fpath, "r", "utf-8") as rf:
                        matches = re.finditer(regex, rf.read(), re.MULTILINE)
                        for matchNum, match in enumerate(matches, start=1):
                            matchStr = match.group(1)
                            addString(matchStr, mappingData)


def addString(matchStr, mappingData):
    for type, strList in mappingData.items():
        if matchStr in strList:
            if allStringDict.get(type) is None:
                allStringDict[type] = []
            if not matchStr in allStringDict[type]:
                allStringDict[type].append(matchStr)


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w+", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    findStr(from_dir)
