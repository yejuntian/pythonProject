import codecs
import os

import lxml.etree as ET

# 新包名字符串集合
replaceDict = {}
# android命名空间约束
android_scheme = "http://schemas.android.com/apk/res/android"

"""
    主要作用：替换应用ApplicationID
"""


def replace_manifest(from_dir, default_package, new_package):
    """
        public_dir:AndroidManifest.xml路径
        default_index：默认包名对应的index
        new_index：新包对应的index
    """
    parseManifest(f"{from_dir}/AndroidManifest.xml", default_package, new_package)
    # print(replaceDict)
    transFile(from_dir)


def transFile(fromDir):
    listdir = os.listdir(fromDir)
    for fname in listdir:
        fpath = os.path.join(fromDir, fname)
        if os.path.isdir(fpath):
            transFile(fpath)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] == "smali":
                print(fpath)
                with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
                    data = rf.read()
                with codecs.open(fpath, mode="w", encoding="utf-8") as wf:
                    for attrOldName, attrNewName in replaceDict.items():
                        data = data.replace(attrOldName, attrNewName)
                    wf.write(data)


# 解析receiver标签
def parseReceiver(root, nameSpace, default_package, new_package):
    for child in root:
        for sub in child:
            if sub.tag == "data":
                attrHost = f"{nameSpace}host"
                hostName = sub.attrib.get(attrHost)
                if hostName is not None:
                    addMapping(hostName, default_package, new_package)
                    sub.attrib[attrHost] = hostName.replace(default_package, new_package)


# 解析provider标签
def parseProvider(sub, nameSpace, default_package, new_package):
    attrAuthorities = f"{nameSpace}authorities"
    authoritiesName = sub.attrib.get(attrAuthorities)
    if authoritiesName is not None:
        if authoritiesName.__contains__(";"):
            authoritiesList = authoritiesName.split(";")
            resultName = ""
            for attrName in authoritiesList:
                addMapping(attrName, default_package, new_package)
                if attrName.__contains__(default_package):
                    if not resultName.__contains__(";"):
                        resultName += f"{attrName};"
                    else:
                        resultName += f"{attrName}"
                else:
                    if not resultName.__contains__(";"):
                        resultName += f"{attrName}2;"
                    else:
                        resultName += f"{attrName}2"
            authoritiesName = resultName
        else:
            addMapping(authoritiesName, default_package, new_package)
        sub.attrib[attrAuthorities] = authoritiesName.replace(default_package, new_package)


# 添加字符串对应关系
def addMapping(attrName, default_package, new_package):
    if isContainsDefaultPackage(attrName, default_package):
        replaceDict[attrName] = attrName.replace(default_package, new_package)
    else:
        replaceDict[attrName] = f"{attrName}2"


def isContainsDefaultPackage(attrName, default_package):
    return attrName.__contains__(default_package)


def parseManifest(fpath, default_package, new_package):
    ET.register_namespace('android', android_scheme)
    nameSpace = "{" + android_scheme + "}"
    tree = ET.parse(fpath)
    root = tree.getroot()
    # print('root-tag:', root.tag, ',root-attrib:', root.attrib, ',root-text:', root.text)
    root.attrib["package"] = new_package
    for child in root:
        # print('child-tag是：', child.tag, ',child.attrib：', child.attrib, ',child.text：', child.text)
        for sub in child:
            if "provider" == sub.tag:
                parseProvider(sub, nameSpace, default_package, new_package)
            elif "receiver" == sub.tag:
                parseReceiver(sub, nameSpace, default_package, new_package)

    data_str = ET.tostring(root, encoding="utf-8").decode('utf-8').replace(' />', '/>')
    write_2_file(fpath, data_str)


def write_2_file(file_path, data_str):
    xml_data = f'<?xml version="1.0" encoding="utf-8" standalone="no"?>{data_str}'
    try:
        with codecs.open(file_path, mode='w+', encoding="utf-8") as f:
            f.write(xml_data)
    except Exception as result:
        print(f"写入{file_path}异常: {result}")


if __name__ == '__main__':
    from_dir = "/Users/shareit/work/shareit/Snaptube_v72050310/DecodeCode/Snaptube_v72050310"
    replace_manifest(from_dir, "com.snaptube.premium", "com.dj.quotepulse")
    print(f"替换AndroidManifest执行完毕，输出到：{from_dir}")
