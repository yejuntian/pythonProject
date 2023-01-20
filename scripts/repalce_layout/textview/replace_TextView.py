import codecs
import os
import xml.etree.ElementTree as ET

oldStr = "<TextView"
replaceStr = "<com.gbwhatsapp.yo.tf"
file_list = []


def replaceText(from_dir, dataList):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            replaceText(fpath, dataList)
        elif os.path.isfile(fpath) and fname.split(".")[-1] == "xml":
            if fname in dataList:
                startReplaceXml(fpath, fname)


def startReplaceXml(file_path, fileName):
    with codecs.open(file_path, encoding="utf-8", mode="r") as rf:
        data = rf.read()
    with codecs.open(file_path, "w", "utf-8") as wfile:
        count = data.count(oldStr)
        if count > 0:
            file_list.append(fileName)
            data = data.replace(oldStr, replaceStr)
        wfile.write(data)


def printResult(dataList, dir_path):
    data = []
    for fname in dataList:
        if fname not in file_list:
            data.append(fname)
    if len(data) > 0:
        print(f"没有执行到的文件列表为：{data}")
    print(f"执行完毕，输出结果保存到：{dir_path}")


def loadData(path):
    parse = ET.parse(path)
    root = parse.getroot()
    data_list = []
    for child in root:
        data_list.append(child.text)
    return data_list


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.22.24.78"
    dataList = loadData("TextView.xml")
    replaceText(f"{from_dir}/res", dataList)
    printResult(dataList, f"{from_dir}/res")
