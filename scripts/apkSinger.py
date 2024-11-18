import os
import zipfile

"""
主要作用：手动解包并重组 .apkm 文件 为没有签名的apk文件，如果想要安装使用需要进行二次签名处理。
"""


def extract_apkm(apkm_file, output_dir):
    """
    解压 .apkm 文件到指定目录
    """
    if not os.path.exists(apkm_file):
        print(f"文件 {apkm_file} 不存在！")
        return False

    if not zipfile.is_zipfile(apkm_file):
        print(f"{apkm_file} 不是有效的 ZIP 文件。")
        return False

    # 解压到指定目录
    with zipfile.ZipFile(apkm_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
        print(f"{apkm_file} 解压到 {output_dir} 成功！")
    return True


def merge_and_repack(apks_dir, output_apk):
    """
    合并主 APK 和配置文件并生成最终的 APK 文件
    """
    # 查找主 APK
    base_apk = None
    for file in os.listdir(apks_dir):
        if file.endswith(".apk") and "base" in file:
            base_apk = os.path.join(apks_dir, file)
            break

    if not base_apk:
        print("未找到主 APK 文件！")
        return False

    # 创建新的 ZIP 文件
    with zipfile.ZipFile(output_apk, 'w') as apk_zip:
        # 添加主 APK 文件
        with zipfile.ZipFile(base_apk, 'r') as base_zip:
            for file in base_zip.namelist():
                apk_zip.writestr(file, base_zip.read(file))

        # 添加其他 APK 文件（如配置文件）
        for file in os.listdir(apks_dir):
            if file.endswith(".apk") and file != os.path.basename(base_apk):
                config_apk = os.path.join(apks_dir, file)
                with zipfile.ZipFile(config_apk, 'r') as config_zip:
                    for file in config_zip.namelist():
                        # 避免文件名冲突
                        if file not in apk_zip.namelist():
                            apk_zip.writestr(file, config_zip.read(file))

    print(f"合并完成！生成的 APK 文件为：{output_apk}")
    return True


def main(apkm_file, output_dir):
    final_apk = f"{os.path.basename(apkm_file).split('.apk')[0]}.apk"  # 最终生成的 APK 文件

    # 创建临时目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 解压 .apkm 文件
    if extract_apkm(apkm_file, output_dir):
        # 合并并重新打包为 APK
        if merge_and_repack(output_dir, final_apk):
            print("所有操作完成！请检查生成的 APK 文件。")
        else:
            print("合并过程中出现问题！")

    # 清理临时目录
    # shutil.rmtree(output_dir)
    # print("清理临时目录完成！")


if __name__ == "__main__":
    apkm_file = "/Users/shareit/Downloads/Whatsapp_2.24.23.78-242378001(arm-v7a).apkm"  # 替换为你的 .apkm 文件路径
    output_dir = "/Users/shareit/Downloads/"  # 解压的临时目录
    main(apkm_file, output_dir)
