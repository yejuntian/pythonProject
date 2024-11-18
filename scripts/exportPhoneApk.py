import os

"""
主要作用：根据自己输入的apk包名，从 Android 设备上导出指定包名对应的apk文件
"""


def run_command(command):
    """使用 os.system 运行命令并返回输出"""
    print(f"执行命令: {command}")
    result = os.system(command)
    if result == 0:
        print("命令执行成功")
        return True
    else:
        print(f"错误: 命令执行失败，返回代码 {result}")
        return False


def find_apk_path(package_name, adb_path="adb"):
    """根据包名获取 APK 路径"""
    command = f'{adb_path} shell pm path {package_name}'
    output = os.popen(command).read().strip()

    if output and "package:" in output:
        apk_path = output.split("package:")[1]
        print(f"找到 APK 路径: {apk_path}")
        return apk_path
    else:
        print(f"未找到包名 {package_name} 对应的 APK 路径。")
        return None


def export_apk_with_adb(apk_path):
    """使用 adb pull 导出指定路径的 APK 文件到默认保存目录"""
    # 获取当前 Python 脚本的所在路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output_dir = os.path.join(script_dir, "exported_apks")

    # 确保导出目录存在，创建目录
    if not os.path.exists(default_output_dir):
        os.makedirs(default_output_dir)
        print(f"创建目录: {default_output_dir}")

    # 构建目标文件路径
    apk_name = os.path.basename(apk_path)  # 提取 APK 文件名
    output_file = os.path.join(default_output_dir, apk_name)

    # 构建 adb pull 命令
    command = f'adb pull {apk_path.strip()} {output_file.strip()}'
    if run_command(command):
        print(f"成功导出 APK 文件到: {output_file}")
    else:
        print("导出失败，请检查路径和设备连接。")


def main():
    package_name = input("请输入APK包名（例如 com.whatsapp）: ").strip()

    if not package_name:
        package_name = "com.whatsapp"

    # 获取 APK 路径
    apk_path = find_apk_path(package_name)

    if apk_path:
        # 导出 APK 文件
        export_apk_with_adb(apk_path)
    else:
        print(f"无法找到包名 {package_name} 对应的 APK 文件路径。")


if __name__ == "__main__":
    main()
