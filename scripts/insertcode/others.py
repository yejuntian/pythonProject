import Utils
from CommonInsert import *


def others():
    return [
        CommonInsert(filePathList=Utils.findFileByName("ContactPickerFragment"),
                     codeFilePath="smali/others/MainBKC",
                     regexList=["const (v\d+), 0x102000a"],
                     rowOffSet=7),

    ]


if __name__ == "__main__":
    for entity in others():
        entity.insertCode()
