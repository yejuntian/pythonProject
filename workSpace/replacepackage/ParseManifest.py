import codecs
import xml.etree.ElementTree as ET
import RenamePackage

manifest = f"{RenamePackage.folder_path}/AndroidManifest.xml"
newManifest = ""
defaultPackage = ""


def getPackageType(package):
    if package == "com.gbwhatsapp":
        return 1
    elif package == "com.obwhatsapp":
        return 2
    elif package == "com.WhatsApp2Plus":
        return 3
    elif package == "com.yowhatsapp":
        return 4
    else:
        return -1


def getPackageSuffix(type):
    if type == 1:
        return "gb"
    elif type == 2:
        return "ob"
    elif type == 3:
        return "plus"
    else:
        return "yo"


def repalcePackageName(defaultPackage, newPackage):
    manifest_index = manifest.rfind('.')
    global newManifest
    newManifest = manifest[:manifest_index] + "_" + getPackageSuffix(getPackageType(newPackage)) + manifest[
                                                                                                       manifest_index:]
    try:
        with codecs.open(manifest, "r", "utf-8") as rf:
            data = rf.read()
        with codecs.open(newManifest, 'w+', "utf-8") as wf:
            print("defaultPackage = " + defaultPackage + " newPackage = " + newPackage)
            print(f"替换{defaultPackage}次数为：{data.count(defaultPackage)} 次")
            data = data.replace(defaultPackage, newPackage)
            wf.write(data)
    except Exception as result:
        print("repalcePackageName 出现异常".center(8, "-"))
        print(result)
    else:
        print(manifest + "-----替换包名完成-----")


def replaceCategory(subLable, newPackage):
    nameSpace = '{http://schemas.android.com/apk/res/android}name'
    for intentFilter in subLable:
        # print('intentFilter-tag是：', intentFilter.tag, ',intentFilter.attrib：', intentFilter.attrib, ',intentFilter.text：', intentFilter.text)
        for sub in intentFilter:
            if sub.tag == "category":
                categoryName = str(sub.attrib[nameSpace])
                if categoryName == defaultPackage:
                    newCategoryName = categoryName.replace(defaultPackage, newPackage)
                    sub.attrib[nameSpace] = newCategoryName
            # print('sub-tag是：', sub.tag, ',sub.attrib：', sub.attrib, ',sub.text：', sub.text)


def replaceSanSdkInfo(type):
    if type == 1:  # gb
        return "6757e179-7b37-4902-a756-792898bbbbe3", "[3.11.4](31104)"
    elif type == 2:  # ob
        # TODO 替换
        return "6757e179-7b37-4902-a756-792898bbbbe3_ob", "[3.11.4](31104)_ob"
    elif type == 3:  # plus
        return "9aa604ef-3f90-42fb-985a-f32d17d5bee3", "[3.8.3](383)"
    else:  # yo
        return "510133b5-d994-47e2-b1b0-df68d7c2b2ac", "[3.6.4](364)"


def replaceApplicationInfo(childLable, type):
    tag = childLable.tag
    if "application" == tag:
        nameSpace = '{http://schemas.android.com/apk/res/android}icon'
        iconType = getPackageSuffix(type)
        if iconType == "gb":
            childLable.attrib[nameSpace] = "@mipmap/icon"
        else:
            childLable.attrib[nameSpace] = "@mipmap/icon_" + iconType


def replaceSanSdk(subLable, type):
    tagLable = subLable.tag
    if "meta-data" == tagLable:
        nameSpace = '{http://schemas.android.com/apk/res/android}'
        sanName = str(subLable.attrib[nameSpace + "name"])
        sanKey, sanValue = replaceSanSdkInfo(type)
        if sanName == "com.san.APP_KEY":
            subLable.attrib[nameSpace + "value"] = sanKey
        elif sanName == "com.san.san-sdk.ver" or sanName == "com.san.san-ex-sdk.ver":
            subLable.attrib[nameSpace + "value"] = sanValue


def parseAndroidManifestXml(oldPackage="com.gbwhatsapp", newPackage="com.yowhatsapp"):
    global defaultPackage
    defaultPackage = oldPackage
    repalcePackageName(defaultPackage, newPackage)
    ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
    global newManifest
    print(newManifest)
    tree = ET.parse(newManifest)
    root = tree.getroot()
    type = getPackageType(newPackage)
    print(f"newPackage = {newPackage} type = {type}")
    # print('root-tag:', root.tag, ',root-attrib:', root.attrib, ',root-text:', root.text)
    for child in root:
        # print('child-tag是：', child.tag, ',child.attrib：', child.attrib, ',child.text：', child.text)
        replaceApplicationInfo(child, type)
        for sub in child:
            # print('sub-tag是：', sub.tag, ',sub.attrib：', sub.attrib, ',sub.text：', sub.text)
            replaceSanSdk(sub, type)

    # tree.write(newManifest, encoding='utf-8', xml_declaration=True, method="xml")
    xml = (bytes('<?xml version="1.0" encoding="utf-8" standalone="no"?>\n', encoding='utf-8') + ET.tostring(root))
    xml = xml.decode('utf-8')
    try:
        with open(newManifest, 'w+') as f:
            f.write(xml)
    except Exception as result:
        print(f"写入{newManifest}出现异常: {result}")
    else:
        print(f"写入{newManifest}完成")
    finally:
        f.close()


if __name__ == '__main__':
    parseAndroidManifestXml("com.gbwhatsapp", "com.yowhatsapp")
