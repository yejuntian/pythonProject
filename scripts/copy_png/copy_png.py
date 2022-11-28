import os
import shutil

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'kotlin', 'lib', 'META-INF', 'original', 'smali',
             'smali_classes2', 'smali_classes3', 'smali_classes4', 'smali_classes5',
             'smali_classes6', 'smali_classes7', 'gen', "raw", "font"]


def copy_png(from_dir, to_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        tpath = os.path.join(to_dir, fname)
        if os.path.isdir(fpath):
            if fname not in blacklist:
                copy_png(fpath, tpath)
        elif os.path.isfile(fpath):
            suffix = fname.split(".")[-1]
            if (not suffix == "xml"
                    and not fname.__contains__(".9.png")
                    and not fname.__contains__(".html")
                    and not fname.__contains__(".json")
                    and not fname.__contains__(".txt")
                    and not fname.__contains__(".tsv")
                    and not fname.__contains__(".yml")
                    and not fname.__contains__(".iml")
                    and not fname.__contains__(".pack")
                    and not fname.__contains__(".zst")
                    and not fname.__contains__(".obi")
                    and not fname.__contains__(".br")
                    and not fname.__contains__(".lottie")
                    and not fname.__contains__(".lottie")
                    and not fname.__contains__(".ttf")
                    and not fname.__contains__(".svg")
                    and not fname.__contains__(".otf")
                    and not fname.__contains__(".properties")
            ):
                if not os.path.exists(to_dir):
                    os.makedirs(to_dir, exist_ok=True)
                shutil.copy(fpath, tpath)


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    to_dir = f"{from_dir}_diff"
    copy_png(from_dir, to_dir)
    print(f"程序执行结束，结果保存在{to_dir}")
