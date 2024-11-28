import xml.etree.ElementTree as ET

"""
 主要检查：com/gbwhatsapp/yo/d1.smali 映射关系是否正确
"""


def parse_file_to_map(file_path):
    result_map = {}
    previous_line = None
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()

                # Check if the line contains a hexadecimal constant (key)
                if line.startswith("const ") and "0x" in line:
                    parts = line.split(",")
                    if len(parts) > 1:
                        previous_line = parts[1].strip()  # Save the hex key

                # Check if the line contains a string constant (value)
                elif line.startswith("const-string"):
                    parts = line.split(",")
                    if len(parts) > 1 and previous_line:
                        string_value = parts[1].strip().strip('"')  # Extract value
                        result_map[previous_line.strip()] = string_value.strip()
                        previous_line = None  # Reset for next pair

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")

    return result_map


def startCheck(mapping, fpath):
    publicMapping = getPublicMapping(fpath)
    keys_to_remove = []  # 用于存储需要删除的键

    # 标记需要删除的键
    for key, value in mapping.items():
        attrName = publicMapping.get(key)
        if attrName and value.lower() == attrName.lower():  # 忽略大小写比较
            keys_to_remove.append(key)

    # 逐个删除标记的键
    for key in keys_to_remove:
        mapping.pop(key)
    if len(mapping) <= 0:
        print("所有映射关系都匹配")
    else:
        print("不匹配的结果如下：")
        print(mapping)


def getPublicMapping(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    tempDict = {}
    for child in root:
        attrId = child.get("id")
        attrName = child.get("name")
        if attrId is not None and attrName is not None:
            tempDict[attrId] = attrName
    return tempDict


# Example usage
if __name__ == "__main__":
    projectPath = "/Users/shareit/work/shareit/gbwhatsapp_2.24.23.78/DecodeCode/Whatsapp_v2.24.23.78"
    mapping = parse_file_to_map(f"{projectPath}/smali_classes7/com/gbwhatsapp/yo/d1.smali")
    startCheck(mapping, f"{projectPath}/res/values/public.xml")
