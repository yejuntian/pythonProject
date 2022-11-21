import argparse
import codecs
import json
import os
import re

foldPath = ""
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin', 'lib', 'META-INF',
             'original', 'res', 'smali', 'smali_classes2', 'smali_classes3',
             'smali_classes4', 'smali_classes7', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["smali"]
savePath = ""
setList = set()
mapList = {}
baseVersion = "2.22.18.70"
newVersion = "2.22.22.80"


def findXClass(from_dir, rexStr):
    fileList = os.listdir(from_dir)
    for fileName in fileList:
        fpath = os.path.join(from_dir, fileName)
        if os.path.isfile(fpath) and fpath.split('.')[-1] in extends:
            print(fpath)
            with codecs.open(fpath, "r", "utf-8") as rfile:
                data = rfile.read()
                findList = re.findall(fr"{rexStr}", data)
                filePath = fpath.split(f"{foldPath}/")[1]
                for findStr in findList:
                    if findStr in mapList:
                        value = mapList[findStr]
                        value.add(filePath)
                    else:
                        classSet = set()
                        classSet.add(filePath)
                        mapList[findStr] = classSet
                setList.update(findList)
        # 如果是文件夹，递归
        elif os.path.isdir(fpath) and fileName not in blacklist:
            findXClass(fpath, rexStr)


def package_data():
    dataList = []
    for newStr in setList:
        newMap = {
            baseVersion: newStr,
            newVersion: "",
            "class": [str for str in mapList[newStr]]
        }
        dataList.append(newMap)
    setList.clear()
    mapList.clear()
    return dataList


def save2File(folder_path, dataList, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("foldPath")
    args = parser.parse_args()

    foldPath = args.foldPath
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
               "|Landroidy/recyclerview/widget/LinearLayoutManager;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/RequestPermissionActivity;->A\w+\(.*?\).+"
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
               "|Lcom/gbwhatsapp/profile/ViewProfilePhoto;->\w+:.*"
               )
    save2File(mCurPath, package_data(), "field.json")
    print("****************查询完毕****************")