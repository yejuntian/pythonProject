import argparse
import xml.etree.ElementTree as ET


# 找出反编译apk中public.xml与反编译项目中public.xml不同的资源属性
# 并把输出结果输出到public_diff.xml中

def parserPublicXml(from_dir, to_dir):
    from_values_xml = from_dir + "/res/values/public.xml"
    to_values_xml = to_dir + "/res/values/public.xml"

    defaultTree = ET.parse(to_values_xml)
    root = defaultTree.getroot()
    defaultResSet = set()
    for child in root:
        defaultResSet.add(child.attrib["name"])

    newResTree = ET.parse(from_values_xml)
    newRoot = newResTree.getroot()

    xmlLable = []
    xmlLable.append('<?xml version="1.0" encoding="utf-8" standalone="no"?>')
    xmlLable.append('<resources>')
    for child in newRoot:
        lableName = child.attrib["name"]
        if lableName not in defaultResSet and "APKTOOL_DUMMY_" not in lableName:
            label = child.attrib['type']
            name = child.attrib['name']
            id = child.attrib['id']
            sub = f'    <public type="{label}" name="{name}" id="{id}" />'
            xmlLable.append(sub)

    xmlLable.append('</resources>')

    newFile = to_values_xml[0:(to_values_xml.rfind("/"))] + "/public_diff.xml"
    print("newFile = " + newFile)
    with open(newFile, 'w+') as wf:
        for line in xmlLable:
            wf.write(line + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    options = parser.parse_args()
    parserPublicXml(options.from_dir, options.to_dir)
