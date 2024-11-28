import os
import json
import xml.etree.ElementTree as ET


def revertString(from_dir, to_dir):
    findStringList = loadString("whatsapp.json")
    print(findStringList)
    fromList = parserXml(f"{from_dir}/res/values/strings.xml",findStringList)
    # toList = parserXml(f"{to_dir}/res/values/strings.xml")


def loadString(fpath):
    with open(fpath, mode="r", encoding="utf-8") as rf:
        data = json.loads(rf.read())
        for key, value in data.items():
            if key == "string":
                return value


def parserXml(fromPath,stringList):
    parser = ET.parse(fromPath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrText = attrib.get("text")
        if attrName in stringList:
            print(attrName)


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.7.81/DecodeCode/Whatsapp_v2.24.7.81"
    revertString(from_dir, to_dir)
