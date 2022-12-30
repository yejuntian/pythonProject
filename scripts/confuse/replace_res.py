import codecs
import json
import os

# 只匹配下面的文件类型
extends = ["xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']


def replaceRes(fpath):
    mappingData = loadData("mapping.json")
    transFolder(fpath, blacklist, mappingData)


def loadData(fpath):
    with codecs.open(fpath, "r", "utf-8") as rf:
        return json.loads(rf.read())


def transFolder(from_dir, blacklist, mappingData):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if fname in blacklist:
            continue
        if os.path.isdir(fpath):
            transFolder(fpath, blacklist, mappingData)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] in extends:
                print(fpath)
                parentFolder = os.path.dirname(fpath)
                parent = parentFolder[parentFolder.rindex("/") + 1:]
                isValuesDir = parent.startswith("values")
                if parent.startswith("layout"):
                    replaceString(fpath, mappingData, True, isValuesDir)
                else:
                    replaceString(fpath, mappingData, False, isValuesDir)


def replaceString(fpath, mappingData, enableRename, isValuesDir):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
    with codecs.open(fpath, "w", "utf-8") as wf:
        replace_times = 0
        for key, value in mappingData.items():
            typeSplit = str(value).split("#")
            if isValuesDir:
                newKey = f'"{key}"'
                newValue = f'"{typeSplit[0]}"'
            else:
                type = typeSplit[-1]
                newKey = f'"@{type}/{key}"'
                newValue = f'"@{type}/{typeSplit[0]}"'
            replace_times += data.count(newKey)
            data = data.replace(newKey, newValue)
        print(r'替换次数：', replace_times)
        wf.write(data)

    if enableRename:
        fname = os.path.basename(fpath).split(".")[0]
        value = mappingData.get(fname)
        if not value is None:
            newFileName = value.split("#")[0]
            newPath = os.path.join(os.path.dirname(fpath), newFileName)
            # print(newPath)
            # os.rename(fpath, newPath)


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    replaceRes(from_dir)
