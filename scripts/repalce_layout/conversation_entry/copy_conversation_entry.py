import codecs
import os
import argparse
import xml.etree.ElementTree as ET


def copyConversationEntry(from_dir, to_dir):
    xmlPath = f"{mCurrentPath}/scripts/repalce_layout/conversation_entry/conversation_entry.xml"
    layoutList = loadFileList(xmlPath)
    transFolderCopy(f"{from_dir}/res/layout", f"{to_dir}/res/layout", layoutList)
    print(f"程序执行结束，结果保存在：{to_dir}/res/layout")


def transFolderCopy(from_dir, to_dir, layoutList):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        tpath = os.path.join(to_dir, fname)
        if os.path.isdir(fpath):
            transFolderCopy(fpath, to_dir, layoutList)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] == "xml" and fname in layoutList:
                with codecs.open(fpath, "r", "utf-8") as rf:
                    data = rf.read()
                with codecs.open(tpath, "w", "utf-8") as wf:
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
    parser.add_argument("to_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    to_dir = args.to_dir
    # from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.22.24.78"
    copyConversationEntry(from_dir, to_dir)
