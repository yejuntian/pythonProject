import argparse
import codecs
import os
import xml.etree.ElementTree as ET

# 存在2个conversation聊天页面样式
isCopyConversation2 = False

"""
    主要作用：copy本项目的res/layout/conversation.xml内容到指定conversation/conversation.xml配置文件中
"""

def copyConversation(from_dir):
    xmlPath = f"{mCurrentPath}/scripts/repalce_layout/conversation/conversation.xml"
    layoutList = loadFileList(xmlPath)
    if not isCopyConversation2:
        data = getConversationData(f"{from_dir}/res/layout/conversation2.xml")
        transFolderCopy(f"{from_dir}/res/layout", layoutList, data)
    else:
        layoutList = [item.replace(".xml", "2.xml") for item in layoutList]
        data = getConversationData(f"{from_dir}/res/layout/conversation2.xml")
        CopyXml(f"{from_dir}/res/layout", layoutList, data)
    print(f"程序执行结束，结果保存在：{from_dir}/res/layout")


def CopyXml(from_dir, layoutList, data):
    if not os.path.exists(from_dir):
        os.makedirs(from_dir)
    for fname in layoutList:
        fpath = os.path.join(from_dir, fname)
        with codecs.open(fpath, "w", "utf-8") as wf:
            wf.write(data)


def getConversationData(fpath):
    with codecs.open(fpath, "r", "utf-8") as rf:
        return rf.read()


def transFolderCopy(from_dir, layoutList, data):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            transFolderCopy(fpath, layoutList, data)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] == "xml" and fname in layoutList:
                with codecs.open(fpath, "w", "utf-8") as wf:
                    wf.write(data)


def loadFileList(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    layoutList = []
    for child in root:
        layoutName = child.text
        if not layoutName is None:
            layoutList.append(layoutName.strip())
    return layoutList


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.20.76/DecodeCode/Whatsapp_v2.23.20.76"
    copyConversation(from_dir)
