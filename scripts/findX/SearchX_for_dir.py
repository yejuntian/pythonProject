import codecs
import json
import os
import re
import argparse
from baseVersion import baseVersion, newVersion

savePath = ""
setList = set()
mapList = {}


def findXClass(folder_path, rexStr):
    fileList = os.listdir(folder_path)
    for fileName in fileList:
        fpath = os.path.join(folder_path, fileName)
        if os.path.isfile(fpath) and fpath.split('.')[-1] == "smali":
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
        elif os.path.isdir(fpath):
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
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{os.path.join(folder_path, fileName)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("foldPath")
    args = parser.parse_args()

    foldPath = args.foldPath
    mCurPath = os.getcwd()
    # 查找类
    findXClass(foldPath, "LX/(?!LX)\w{4};")
    save2File(mCurPath, package_data(setList), "class.json")
    # 清空搜索到的class数据
    setList.clear()
    # 查找方法
    findXClass(foldPath,
               "LX/(?!LX)\w{3};->.*\(.*?\).+"
               "|Lcom/gbwhatsapp/conversationslist/ConversationsFragment;->.*\(.*?\).+"
               "|Lcom/gbwhatsapp/status/playback/fragment/StatusPlaybackContactFragment;->.*\(.*?\).+"
               "|Lcom/gbwhatsapp/HomeActivity;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/status/StatusesFragment;->\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/Conversation;->A\w+\(.*?\).+"
               "|Landroidy/recyclerview/widget/LinearLayoutManager;->\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/RequestPermissionActivity;->\w+\(.*?\).+"
               "|Lcom/airbnb/lottie/LottieAnimationView;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/MuteDialogFragment;->\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/status/ContactStatusThumbnail;->A\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/contact/picker/ContactPickerFragment;->\w+\(.*?\).+"
               "|Lcom/gbwhatsapp/updates/ui/UpdatesFragment;->\w+\(.*?\).+"
               "|Lcom/whatsapp/calling/callhistory/view/CallsHistoryFragmentV2;->\w+\(.*?\).+"
               "|Lcom/whatsapp/calling/callhistory/view/CallsHistoryFragment;->\w+\(.*?\).+"
               "|Lcom/whatsapp/calling/callhistory/CallsHistoryFragment;->\w+\(.*?\).+"
               "|Landroidy/fragment/app/Fragment;->\w+\(.*?\).+"
               )
    # 查找属性
    findXClass(foldPath,
               "LX/(?!LX)\w{3};->.*:.*"
               "|Lcom/gbwhatsapp/conversationslist/ConversationsFragment;->.*:.*"
               "|Lcom/gbwhatsapp/status/playback/fragment/StatusPlaybackContactFragment;->.*:.*"
               "|Lcom/gbwhatsapp/HomeActivity;->A\w+:.*"
               "|Lcom/gbwhatsapp/status/StatusesFragment;->\w+:.*"
               "|Lcom/gbwhatsapp/Conversation;->\w+:.*"
               "|Lcom/gbwhatsapp/profile/ViewProfilePhoto;->\w+:.*"
               "|Lcom/gbwhatsapp/contact/picker/ContactPickerFragment;->\w+:.*"
               "|Lcom/gbwhatsapp/collections/observablelistview/ObservableListView;->\w+:.*"
               "|Lcom/whatsapp/calling/callhistory/CallsHistoryFragment;->\w+:.*"
               "|Lcom/gbwhatsapp/conversationslist/ViewHolder;->A\w+:.*"
               "|Landroidy/recyclerview/widget/RecyclerView;->A\w+:.*"
               "|Lcom/gbwhatsapp/RequestPermissionActivity;->A\w+:.*"
               "|Landroidy/viewpager/widget/ViewPager;->A\w+:.*"
               "|Landroidy/fragment/app/ListFragment;->A\w+:.*"
               "|Lcom/gbwhatsapp/conversationslist/ViewHolder;->A\w+:.*"
               "|Landroidy/recyclerview/widget/RecyclerView;->A\w+:.*"
               "|Lcom/gbwhatsapp/RequestPermissionActivity;->A\w+:.*"
               "|Landroidy/viewpager/widget/ViewPager;->A\w+:.*"
               "|Landroidy/fragment/app/ListFragment;->A\w+:.*"
               "|Lcom/gbwhatsapp/textstatuscomposer/TextStatusComposerActivity;->A\w+:.*"
               "|Lcom/gbwhatsapp/statuscomposer/composer/TextStatusComposerFragment;->A\w+:.*"
               "|Landroidy/fragment/app/Fragment;->A\w+:.*"
               "|Lcom/gbwhatsapp/updates/ui/adapter/UpdatesAdapter;->A\w+:.*"
               )
    save2File(mCurPath, package_data(sorted(setList)), "field_method.json")
    print("****************查询完毕****************")
