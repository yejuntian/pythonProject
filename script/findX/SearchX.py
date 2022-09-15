import codecs
import json
import os
import re

savePath = ""
foldPath = "../../DecodeCode/WhatsApp_v2.22.18.70/smali_classes5"
setList = set()
mapList = {}


def findXClass(folder_path, rexStr):
    os.chdir(folder_path)
    cwd = os.getcwd()
    fileList = os.listdir(cwd)
    for fileName in fileList:
        fpath = os.path.join(cwd, fileName)
        if os.path.isfile(fpath):
            with codecs.open(fpath, "r", "utf-8") as rfile:
                data = rfile.read()
                findList = re.findall(fr"{rexStr}", data)
                for findStr in findList:
                    if findStr in mapList:
                        value = mapList[findStr]
                        value.add(fileName)
                    else:
                        classSet = set()
                        classSet.add(fileName)
                        mapList[findStr] = classSet
                setList.update(findList)
        # 如果是文件夹，递归
        elif os.path.isdir(fpath):
            findXClass(fpath, rexStr)


def package_data():
    dataList = []
    for newStr in setList:
        newMap = {
            "2.22.10.73": newStr,
            "2.22.18.70":"",
            "class": [str for str in mapList[newStr]]
        }
        dataList.append(newMap)
    setList.clear()
    mapList.clear()
    return dataList


def save2File(folder_path, dataList, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=4)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)


if __name__ == "__main__":
    mCurPath = os.getcwd()
    # 查找类
    findXClass(foldPath, "LX/\w*;")
    save2File(mCurPath, package_data(), "class.json")
    # 查找方法
    findXClass(foldPath,
               "LX/\w*;->.*\(.*?\).+"
                "|ConversationsFragment;->.*\(.*?\).+"
                "|StatusPlaybackContactFragment;->.*\(.*?\).+"
                "|HomeActivity;->A\w+\(.*?\).+"
                "|StatusesFragment;->A\w+\(.*?\).+"
                "|Lcom/gbwhatsapp/Conversation;->A\w+\(.*?\).+"
               )
    save2File(mCurPath, package_data(), "method.json")
    # 查找属性
    findXClass(foldPath,
               "LX/\w+;->.*:.*"
               "|ConversationsFragment;->.*:.*"
               "|StatusPlaybackContactFragment;->.*:.*"
               "|HomeActivity;->A\w+:.*"
               "|StatusesFragment;->\w+:.*"
               "|Lcom/gbwhatsapp/Conversation;->\w+:.*"
               )
    save2File(mCurPath, package_data(), "field.json")
    print("****************查询完毕****************")
