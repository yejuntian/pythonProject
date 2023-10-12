import codecs
import json
import os
import argparse
import xml.etree.ElementTree as ET

# 用来保存匹配到的xml映射关系
layoutMappingDic = {}
# 用来保存没有匹配到的对应关系
notFondLayoutDic = {}

"""
    主要作用：根据matchCondition文件夹下json文件，根据json内容进行匹配，查找res/layout对应的xml文件名称。
"""


def main(folderPath):
    currentPath = os.getcwd()
    # 缓存XML内容
    xml_cache = cacheContents(folderPath)
    jsonCache = cacheContents(f"{currentPath}/scripts/res/match_layout/matchCondition")
    filterData(xml_cache, jsonCache)
    save_2_file(json.dumps(layoutMappingDic, ensure_ascii=False, indent=2),
                f"{currentPath}/scripts/values/replace_layout", "layout.json")
    print("*************没有匹配到的xml如下所示：*************")
    print(notFondLayoutDic)


def save_2_file(jsonStr, fpath, fileName):
    newPath = os.path.join(fpath, fileName)
    with open(newPath, "w+") as wf:
        wf.write(jsonStr)
    print(f"匹配结果保存到：{newPath}")


# 过滤数据
def filterData(xml_cache, jsonCache):
    tempDic = {}
    for fName, jsonContent in jsonCache.items():
        layoutName = fName.split(".json")[0]
        tempDic[layoutName] = []
        # 从缓存中查找匹配的XML文件
        matching_files = find_matching_xml_files_from_cache(xml_cache, json.loads(jsonContent))
        for file_name, xmlContent in matching_files:
            mappingLayoutName = file_name.split(".xml")[0]
            tempDic[layoutName].append(mappingLayoutName)
            # print(f"{fName}-->{file_name}")
    # 对数据进行二次筛选
    for layoutName, mappingLayoutNameList in tempDic.items():
        if mappingLayoutNameList is not None and len(mappingLayoutNameList) == 1:
            layoutMappingDic[mappingLayoutNameList[0]] = layoutName
        else:
            notFondLayoutDic[layoutName] = mappingLayoutNameList


def cacheContents(folder_path):
    xml_cache = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".xml") or file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                with codecs.open(file_path, 'r', encoding="utf-8") as file:
                    xml_content = file.read()
                    xml_cache[file_name] = xml_content
    return xml_cache


def find_matching_xml_files_from_cache(xml_cache, conditions):
    matching_files = []

    for file_name, xml_content in xml_cache.items():
        all_condition_matches = True  # 初始化为True，用于“全部”条件逻辑

        for condition in conditions:
            condition_value = condition["matchStr"]
            notCondition_value = condition.get("notContainsStr")

            # 检查condition_value是否存在于XML内容中
            condition_match = condition_value in xml_content

            # 检查notCondition_value是否不存在于XML内容中，如果存在的话
            if notCondition_value:
                not_condition_match = notCondition_value not in xml_content
            else:
                not_condition_match = True  # 如果notCondition_value未指定，将其视为匹配

            # 使用当前条件结果更新all_condition_matches
            all_condition_matches = all_condition_matches and condition_match and not_condition_match

        if all_condition_matches:
            matching_files.append((file_name, xml_content))

    return matching_files


def loadData(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    data_list = []
    for child in root:
        name = child.text
        data_list.append(name.split(".")[0])
    return data_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path")
    args = parser.parse_args()
    project_path = args.project_path

    # project_path = "/Users/shareit/work/shareit/gbwhatsapp_2.23.19.82/DecodeCode/Whatsapp_v2.23.19.82"
    main(f"{project_path}/res/layout")
