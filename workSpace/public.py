import argparse
import xml.etree.ElementTree as etree


#用于存放每种类型的最大值key是类型value是最大值
max_dict = {}
#key是类型value是名字集合
name_dict= {}


#解析wa的
def copy(from_dir,to_dir):
    from_public = from_dir+"/res/values/public.xml"
    to_public = to_dir+"/res/values/public.xml"
    to_tree = etree.parse(to_public)
    for child in to_tree.getroot():
        if(child.tag=="public" and "id" in child.attrib):
            name=child.attrib['name']
            type=child.attrib['type']
            id=child.attrib['id']
            if(type in name_dict):
                pass
            else:
                name_dict[type] = []
            name_dict[type].append(name)
            #十六进制转十进制
            id = int(id,16) 
            if(type in max_dict):
                if(id > int(max_dict[type].attrib['id'],16)):
                    max_dict[type] = child
            else:
                max_dict[type] = child
    from_tree = etree.parse(from_public)
    for child in from_tree.getroot():
        if(child.tag=="public" and "id" in child.attrib):
            name=child.attrib['name']
            type=child.attrib['type']
             #屏蔽APKTOOL开头的name
            if(name not in name_dict[type] and "APKTOOL" not in name):
                max = max_dict[type]
                child.set('id',str(hex(int(max.attrib['id'],16)+1)))
                max_dict[type] = child
                index=to_tree.getroot().index(max)
                to_tree.getroot().insert(index+1,child)
    # to_tree.write(to_public,encoding="utf-8",method="xml",pretty_print=True,xml_declaration=True,with_tail=True,strip_text=False)



if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("from_dir")
    # parser.add_argument("to_dir")
    # options = parser.parse_args()
    # copy(options.from_dir,options.to_dir)
    copy("", "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.7.74")