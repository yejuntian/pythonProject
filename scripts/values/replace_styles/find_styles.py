import json
import os
import xml.etree.ElementTree as ET

flagList = ["@color", "@dimen", "@integer", "@bool"]
# style.xml对应关系
stylesMapping = {}
# *********下面是to_dir 相关集合*************
# 所有colors.xml映射集合
allColorValues = {}
# 所有dimens.xml映射集合
allDimensValues = {}
# 所有integers.xml映射集合
allIntegersValues = {}
# 所有bools.xml映射集合
allBoolsValues = {}
# 所有styles.xml映射集合
allStyleValues = {}
# styles.xml 映射list集合
newStylesEntityList = []
# style 属性name集合列表
newStylesNameList = []
# style子元素个数集合列表
newStylesChildCountList = []
# *********下面是from_dir 相关集合*************
# 所有colors.xml映射集合
oldColorValues = {}
# 所有dimens.xml映射集合
oldDimensValues = {}
# 所有integers.xml映射集合
oldIntegersValues = {}
# 所有bools.xml映射集合
oldBoolsValues = {}
# 所有styles.xml映射集合
oldStyleValues = {}
# styles.xml 映射list集合
oldStylesEntityList = []
# style 属性name集合列表
oldStylesNameList = []
# style子元素个数集合列表
oldStylesChildCountList = []
# 是否保存文件
isSaveFile = False


class StylesEntity:
    def __init__(self, name, parent, hasParent, number, childCount, itemMapping, keys, values):
        self.name = name
        self.parent = parent
        self.hasParent = hasParent
        self.number = number
        self.childCount = childCount
        self.itemMapping = itemMapping
        self.keys = keys
        self.values = values


def findStyle(from_dir, to_dir):
    findNewMappingStyles(to_dir)
    findOldMappingStyles(from_dir)
    matchCorrectStyle(newStylesEntityList, oldStylesEntityList)
    save2File(stylesMapping, os.getcwd(), "mapping.json")
    print(f"对应关系个数：{len(stylesMapping)}")


# 匹配style对应关系
def matchCorrectStyle(newEntityList, oldEntityList):
    for entity in newEntityList:
        name = entity.name
        parent = entity.parent
        hasParent = entity.hasParent
        childCount = entity.childCount
        itemMapping = entity.itemMapping

        if childCount <= 0:
            continue
        count = newStylesChildCountList.count(childCount)
        old_count = oldStylesChildCountList.count(childCount)
        if count == 1 and old_count == 1:  # TODO 唯一style,有些个数相同但是item不匹配，需要进行逻辑优化
            pos = oldStylesChildCountList.index(childCount)
            oldEntity = oldEntityList[pos]
            old_name = oldEntity.name
            old_parent = oldEntity.parent
            old_hasParent = oldEntity.hasParent
            old_itemMapping = oldEntity.itemMapping

            if hasParent == old_hasParent:
                if parent.__contains__("$") and old_parent.__contains__("$"):
                    parent = parent.split("$")[0]
                    old_parent = old_parent.split("$")[0]
                saveStylesMapping(name, old_name)
                saveStylesMapping(parent, old_parent)
            matchItemStyle(name, old_name, itemMapping, old_itemMapping)
        else:
            # print(f"name = {name} childCount = {childCount}")
            cmpChildContent(entity, oldEntityList, hasParent, childCount, newEntityList)


# 比较item内容
def cmpChildContent(entity, oldEntityList, hasParent, childCount, newEntityList):
    parent = entity.parent
    number = entity.number
    newKeys = entity.keys
    newValues = entity.values

    entityMapping = {}
    for pos, oldEntity in enumerate(oldEntityList):
        old_hasParent = oldEntity.hasParent
        old_childCount = oldEntity.childCount
        old_parent = oldEntity.parent
        old_number = oldEntity.number
        oldKeys = oldEntity.keys
        oldValues = oldEntity.values
        if hasParent == old_hasParent and childCount == old_childCount:
            name = entity.name
            old_name = oldEntity.name

            if childCount == 1:
                if newKeys == oldKeys and newValues == oldValues and number == old_number:
                    if not parent is None and not old_parent is None:
                        if parent.__contains__("$") and old_parent.__contains__("$"):
                            addMapping(entityMapping, entity, oldEntity)
                        else:
                            if parent == old_parent:
                                addMapping(entityMapping, entity, oldEntity)
                    else:
                        if parent == old_parent:
                            addMapping(entityMapping, entity, oldEntity)
            else:
                if newValues == oldValues and number == old_number:
                    if not parent is None and not old_parent is None:
                        if parent.__contains__("$") and old_parent.__contains__("$"):
                            addMapping(entityMapping, entity, oldEntity)
                        else:
                            if parent == old_parent:
                                addMapping(entityMapping, entity, oldEntity)
                    else:
                        if parent == old_parent:
                            addMapping(entityMapping, entity, oldEntity)

    # 添加Styles对应关系
    addStylesMapping(entityMapping)


def addMapping(map, entity, oldEntity):
    count1Value = map.get(entity)
    if count1Value is None:
        map[entity] = []
    map[entity].append(oldEntity)
    # print(f"name = {entity.name} name2 = {oldEntity.name}")


def addStylesMapping(dataMap):
    for entity, oldEntityList in dataMap.items():
        if len(oldEntityList) > 1:
            print(f"匹配多个 name = {entity.name}")
            continue
        oldEntity = oldEntityList[0]
        name = entity.name
        parent = entity.parent
        hasParent = entity.hasParent
        itemMapping = entity.itemMapping

        old_name = oldEntity.name
        old_parent = oldEntity.parent
        old_hasParent = oldEntity.hasParent
        old_itemMapping = oldEntity.itemMapping

        # 保存parent对应关系
        if hasParent == old_hasParent:
            if not parent is None and not old_parent is None:
                if parent.__contains__("$") and old_parent.__contains__("$"):
                    parent = parent.split("$")[0]
                    old_parent = old_parent.split("$")[0]
                    saveStylesMapping(parent, old_parent)

                    parent2 = parent.split("$")[0]
                    old_parent2 = old_parent.split("$")[0]
                    saveStylesMapping(parent2, old_parent2)
                else:
                    saveStylesMapping(parent, old_parent)
        # 保存name对应关系
        saveStylesMapping(name, old_name)
        matchItemStyle(name, old_name, itemMapping, old_itemMapping)
    # print(f"name = {entity.name} name2 = {oldEntityList[0].name} size = {len(oldEntityList)}")


def matchItemStyle(name, old_name, itemMapping, old_itemMapping):
    # print(f"name = {name} oldName = {old_name}")
    old_keyList = list(old_itemMapping.keys())
    old_valueList = list(old_itemMapping.values())
    for index, key, in enumerate(itemMapping):
        value = itemMapping[key]
        old_key = old_keyList[index]
        old_value = old_valueList[index]

        if value.startswith("?APKTOOL"):
            attr_color = value.split("?")[1]
            old_attr_color = old_value.split("?")[1]
            # print(f"attr_color = {attr_color} old_attr_color = {old_attr_color}")
            saveStylesMapping(attr_color, old_attr_color)
        elif value.startswith("@style/"):
            styleName = getStyleName(value)
            old_styleName = getStyleName(old_value)
            # print(f"styleName = {styleName} old_styleName = {old_styleName}")
            saveStylesMapping(styleName, old_styleName)
        # print(f"index = {index} key = {key} old_key = {old_key} value = {value}")


def getStyleName(value):
    if value.__contains__("$"):
        value = value.split("$")[0]
    return value.split("/")[1]


def saveStylesMapping(key, value):
    if key.__contains__("@style/"):
        key = key.split("/")[1]

    if value.__contains__("@style/"):
        value = value.split("/")[1]

    if stylesMapping.get(key) is None and not value in stylesMapping.values():
        stylesMapping[key] = value


# 查找to_dir相关xml对应关系
def findNewMappingStyles(to_dir):
    colorsPath = f"{to_dir}/res/values/colors.xml"
    dimensPath = f"{to_dir}/res/values/dimens.xml"
    integersPath = f"{to_dir}/res/values/integers.xml"
    boolsPath = f"{to_dir}/res/values/bools.xml"
    setMapValues(colorsPath, allColorValues, "colors.json", flagList[0])
    setMapValues(dimensPath, allDimensValues, "dimens.json", flagList[1])
    setMapValues(integersPath, allIntegersValues, "integers.json", flagList[2])
    setMapValues(boolsPath, allBoolsValues, "bools.json", flagList[3])
    newStylesPath = f"{to_dir}/res/values/styles.xml"
    parserStyles(newStylesPath, "map_new_styles.json", False)


# 查找from_dir相关xml对应关系
def findOldMappingStyles(from_dir):
    colorsPath = f"{from_dir}/res/values/colors.xml"
    dimensPath = f"{from_dir}/res/values/dimens.xml"
    integersPath = f"{from_dir}/res/values/integers.xml"
    boolsPath = f"{from_dir}/res/values/bools.xml"
    setMapValues(colorsPath, oldColorValues, "colors_old.json", flagList[0])
    setMapValues(dimensPath, oldDimensValues, "dimens_old.json", flagList[1])
    setMapValues(integersPath, oldIntegersValues, "integers_old.json", flagList[2])
    setMapValues(boolsPath, oldBoolsValues, "bools_old.json", flagList[3])

    oldStylesPath = f"{from_dir}/res/values/styles.xml"
    parserStyles(oldStylesPath, "map_old_styles.json", True)


# 设置映射关系
def setMapValues(fpath, styleMap, saveFileName, tag):
    tag = f"{tag}/"
    parser = ET.parse(fpath)
    root = parser.getroot()
    valueMapping = {}
    for child in root:
        attrib = child.attrib
        colorName = attrib.get("name")
        valueMapping[colorName] = child.text
    addXmlMapping(fpath, valueMapping, tag, styleMap, saveFileName)


def addXmlMapping(fpath, valueMapping, tag, styleMap, saveFileName):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")

        mCurValue = child.text.strip()
        if mCurValue.startswith(tag):
            mCurValue = getValues(mCurValue, valueMapping, tag)
        styleMap[attrName] = mCurValue

    if isSaveFile:
        save2File(styleMap, os.getcwd(), saveFileName)


# 获取value值
def getValues(colorTxt, dataMapping, tag):
    if colorTxt.startswith(tag):
        colorName = colorTxt.split("/")[1]
        colorValue = dataMapping.get(colorName)
        while colorValue.startswith(tag):
            colorName = colorValue.split("/")[1]
            colorValue = dataMapping.get(colorName)
        return f"{colorTxt}${colorValue}"
    return colorTxt


def save2File(styleMap, folder_path, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(styleMap, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


def parserStyles(fpath, saveFileName, isFromDir):
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        childName = attrib.get("name")
        childParent = attrib.get("parent")
        if not isFromDir:
            allStyleValues[childName] = childParent
        else:
            oldStyleValues[childName] = childParent

    if isSaveFile:
        if not isFromDir:
            save2File(allStyleValues, os.getcwd(), "styles.json")
        else:
            save2File(oldStyleValues, os.getcwd(), "styles_old.json")

    addStyleMapping(fpath, saveFileName, isFromDir)


# 添加映射关系
def addStyleMapping(fpath, saveFileName, isFromDir):
    parser = ET.parse(fpath)
    root = parser.getroot()
    size = len(root)
    for pos, child in enumerate(root):
        attrib = child.attrib
        childName = attrib.get("name")
        childParent = attrib.get("parent")

        if pos == 0:
            preCount = 0
            nextCount = len(root[pos + 1])
            curCount = len(child)
        elif pos == size - 1:
            preCount = len(root[pos - 1])
            nextCount = 0
            curCount = len(child)
        else:
            preCount = len(root[pos - 1])
            nextCount = len(root[pos + 1])
            curCount = len(child)
        count = f"{preCount}_{curCount}_{nextCount}"

        # 获取superParent
        hasParent = not childParent is None
        if hasParent and childParent.startswith("@style/"):
            name = childParent.split("/")[1]
            styleValues = allStyleValues if not isFromDir else oldStyleValues
            superParent = styleValues.get(name)
            if not superParent is None and not superParent == "":
                childParent = getStyleParent(childParent, superParent, styleValues)

        itemMapping = {}
        for subChild in child:
            subAttrib = subChild.attrib
            subChildName = subAttrib.get("name")
            subChildContent = getSubChildContent(subChild, childName, isFromDir)
            itemMapping[subChildName] = subChildContent

        entity = StylesEntity(childName, childParent, hasParent, count, len(itemMapping),
                              itemMapping, getStyleKeys(itemMapping), getStyleValues(itemMapping))
        if not isFromDir:
            newStylesEntityList.append(entity)
        else:
            oldStylesEntityList.append(entity)

    dataList = []
    styleList = newStylesEntityList if not isFromDir else oldStylesEntityList
    nameList = newStylesNameList if not isFromDir else oldStylesNameList
    childCountList = newStylesChildCountList if not isFromDir else oldStylesChildCountList
    for entity in styleList:
        dataMapping = {"name": entity.name, "parent": entity.parent, "hasParent": entity.hasParent,
                       "number": entity.number, "childCount": entity.childCount, "itemMapping": entity.itemMapping,
                       "keys": entity.keys, "values": entity.values}
        dataList.append(dataMapping)
        nameList.append(entity.name)
        childCountList.append(entity.childCount)

    if isSaveFile:
        save2File(dataList, os.getcwd(), saveFileName)


def getStyleKeys(itemMapping):
    keys = itemMapping.keys()
    str = ""
    for item in keys:
        str += item + "%"
    # print(f"keys = {str}")
    return str


def getStyleValues(itemMapping):
    values = itemMapping.values()
    str = ""
    for item in values:
        if item.__contains__("$"):
            item = item.split("$")[1]
        str += item + "%"
    # print(f"values = {str}")
    return str


def getSubChildContent(subChild, childName, isFromDir):
    content = subChild.text
    newContent = content
    if content.__contains__("/"):
        content_split = content.split("/")
        flag = content_split[0]
        name = content_split[1]
        if flag == "@color":
            values = allColorValues if not isFromDir else oldColorValues
            content = getStyleItemValue(values, name, newContent)
        elif flag == "@dimen":
            values = allDimensValues if not isFromDir else oldDimensValues
            content = getStyleItemValue(values, name, newContent)
        elif flag == "@integer":
            values = allIntegersValues if not isFromDir else oldIntegersValues
            content = getStyleItemValue(values, name, newContent)
        elif flag == "@bool":
            values = allBoolsValues if not isFromDir else oldBoolsValues
            content = getStyleItemValue(values, name, newContent)
        elif flag == "@style":
            values = allStyleValues if not isFromDir else oldStyleValues
            curStyle = values.get(name)
            if curStyle == "None" or curStyle is None:
                # print(f" childName = {childName} subChild = {ET.tostring(subChild)}")
                return newContent
            else:
                content = getStyleParent(newContent, curStyle, values)
    return newContent if content is None else content


# 获取style parent
def getStyleParent(content, curStyle, values):
    if curStyle == "":
        return content
    while curStyle.startswith("@style/"):
        name = curStyle.split("/")[1]
        value = values.get(name)
        if not value is None and not value == "":
            curStyle = values.get(name)
        else:
            break
    # print(f"{content}${curStyle}")
    return f"{content}${curStyle}"


def getStyleItemValue(map, key, newContent):
    value = str(map.get(key))
    if value == "None":
        return newContent
    if not value.__contains__("$"):
        value = f"{key}${value}"
    return value


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.15.81/DecodeCode/Whatsapp_v2.23.15.81"
    findStyle(from_dir, to_dir)
