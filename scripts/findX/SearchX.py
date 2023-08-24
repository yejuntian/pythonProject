import argparse
import codecs
import json
import os
import re

foldPath = ""
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin', 'lib', 'META-INF',
             'original', 'res', 'smali', 'smali_classes2', 'smali_classes3',
             'smali_classes4', 'smali_classes5', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["smali"]
savePath = f"{os.getcwd()}/scripts/findX"
setList = set()
mapList = {}
from baseVersion import baseVersion, newVersion


def findXClass(from_dir, rexStr):
    fileList = os.listdir(from_dir)
    for fileName in fileList:
        fpath = os.path.join(from_dir, fileName)
        if os.path.isfile(fpath) and fpath.split('.')[-1] in extends:
            # print(fpath)
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


def package_data(searchList):
    dataList = []
    sorted_list = sorted(searchList)
    sorted_list.sort()
    for newStr in sorted_list:
        newMap = {
            baseVersion: newStr,
            newVersion: "",
            "class": sorted([str for str in mapList[newStr]])
        }
        dataList.append(newMap)
    searchList.clear()
    mapList.clear()
    return dataList


def save2File(folder_path, dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    fpath = os.path.join(folder_path, fileName)
    with open(fpath, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{fpath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("foldPath")
    args = parser.parse_args()

    foldPath = args.foldPath
    # 查找类
    findXClass(foldPath, "LX/\w*;")
    save2File(savePath, package_data(setList), "class.json")
    # 清空搜索到的class数据
    setList.clear()
    # 查找方法
    findXClass(foldPath,
               "LX/\w*;->.*\(.*?\).+"
               "|Lcom/gbwhatsapp/conversationslist/ConversationsFragment;->.*\(.*?\).+"
               "|Lcom/gbwhatsapp/status/playback/fragment/StatusPlaybackContactFragment;->.*\(.*?\).+"
               "|Lcom/gbwhatsapp/HomeActivity;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/status/StatusesFragment;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/Conversation;->A\w+\(.*?\).+"
               "|Landroidy/recyclerview/widget/LinearLayoutManager;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/RequestPermissionActivity;->A\w+\(.*?\).+"
               "|Lcom/airbnb/lottie/LottieAnimationView;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/MuteDialogFragment;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/status/ContactStatusThumbnail;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/contact/picker/ContactPickerFragment;->A\w+\(.*?\).+"
               )
    # 查找属性
    findXClass(foldPath,
               "LX/\w+;->.*:.*"
               "|Lcom/gbwhatsapp/conversationslist/ConversationsFragment;->.*:.*"
               "|Lcom/gbwhatsapp/status/playback/fragment/StatusPlaybackContactFragment;->.*:.*"
               "|Lcom/gbwhatsapp/HomeActivity;->A\w+:.*"
               "|Lcom/gbwhatsapp/status/StatusesFragment;->\w+:.*"
               "|Lcom/gbwhatsapp/Conversation;->\w+:.*"
               "|Lcom/gbwhatsapp/profile/ViewProfilePhoto;->\w+:.*"
               "|Lcom/gbwhatsapp/contact/picker/ContactPickerFragment;->\w+:.*"
               "|Lcom/gbwhatsapp/collections/observablelistview/ObservableListView;->\w+:.*"
               )
    save2File(savePath, package_data(sorted(setList)), "field_method.json")
    print("****************查询完毕****************")
