import Utils
from CommonInsert import *


# 获取x()所需参数
def getXParam(matches):
    for match in matches:
        line = match.group(1)
        param = match.group(2)
        return line, param


# 获取需要替换为x()所在行
paramStr = getParam(
    "This Activity already has an action bar supplied by the window decor. Do not request Window.FEATURE_SUPPORT_ACTION_BAR and set windowActionBar to false in your theme to use a Toolbar instead.",
    regexList=["invoke\-virtual \{.*\}\, (.*\-\>(.*)LX\/.*)",
               "move\-result\-object v\d",
               "invoke\-virtual \{.*\}\, Landroid\/app\/Activity\;\-\>getWindow\(\)Landroid\/view\/Window\;"]
    , func=getXParam)


def getXFormatCode(codeStr, match):
    param1 = match.group(1)
    param2 = match.group(2)
    if param1 is not None and param2 is not None:
        param2 = param2.replace(paramStr[1], "x()")
        return codeStr.format(param1=param1, param2=param2)
    return None


def others():
    return [
        CommonInsert(filePathList=Utils.findFileByName("ContactPickerFragment"),
                     codeFilePath="smali/others/MainBKC",
                     regexList=["const v\d+, 0x102000a",
                                matchLine,
                                "move\-result\-object v\d+",
                                "check\-cast (v\d+)\, Landroid\/widget\/ListView\;"],
                     rowOffSet=0),

        CommonInsert(filePathList=getTransFileList(paramStr[0]),
                     codeFilePath="smali/others/x",
                     regexList=[r"invoke\-virtual \{(.*)\}\, " + f"({re.escape(paramStr[0])})"],
                     rowOffSet=0,
                     code=getXFormatCode),

        CommonInsert(filePathList=Utils.findXByStr(
            "This Activity already has an action bar supplied by the window decor. Do not request Window.FEATURE_SUPPORT_ACTION_BAR and set windowActionBar to false in your theme to use a Toolbar instead."),
            codeFilePath="smali/others/method",
            rowOffSet=insertFileEnd),
    ]


if __name__ == "__main__":
    objectList = others()
    for entity in objectList:
        entity.insertCode()
    print(paramStr)
