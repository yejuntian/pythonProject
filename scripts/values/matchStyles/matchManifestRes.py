import os
import json
import xml.etree.ElementTree as ET


def findResMapping(from_path, to_path):
    parserXml(to_path)


def parserXml(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        tag = child.tag
        if tag == "queries":
            pass
        elif tag == "application":
            print(str(attrib))


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.8.76/AndroidManifest.xml"
    to_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80/AndroidManifest.xml"
    findResMapping(from_dir, to_dir)
