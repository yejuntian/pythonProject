import glob
import re
from smali.statements import Statement
from smali.statements import FieldStatement

old_dir = "/WhatsApp_v2.22.7.74"

new_dir = "/Users/shareit/Work/wagb/DecodeCode/WhatsApp_v2.22.17.2"

def search_string():
    #搜索X目录下的所有smali文件中的字符串
    dict = {}
    files= glob.glob(old_dir+"/"+"smali*/X/*.smali",recursive=True)
    print(files)
    for file in files:
        with open(file, 'r') as f:
            l = re.findall(r'".*"', f.read())
            for item in l:
                if(item not in dict):
                    s = set()
                    s.add(file)
                    dict[item] = s
                else:
                    dict[item].add(file)
    print("字符串个数："+str(len(dict)))
    #过滤到有重复的字符串
    dict = {k: v for k, v in dict.items() if len(v) ==1}
    print("过滤之后字符串个数："+str(len(dict)))
    return dict

def search_lx():
    #定义一个set去重
    s = set()
    #搜索yo和yobasha目录的smali文件中的LX类
    smali_file = glob.glob(old_dir+"/"+"smali*/com/gbwhatsapp/yo*/**/*.smali",recursive=True)
    for fp in smali_file:
        with open(fp, 'r') as f:
            l = re.findall(r'LX/\w*;', f.read())
            s.update(l)
    #遍历所有的LX类
    print("LX类个数："+str(len(s)))
    return s

#x和字符串对应关系
def x_s(s,dict):
    d = {}
    for i in s:
        i = i.split('/')[1].replace(';','')
        files = glob.glob(old_dir+"/"+"smali*/**/"+i+"*.smali",recursive=True)
        if len(files)==1:
            with open(files[0], 'r') as f:
                l = re.findall(r'".*"', f.read())
                for j in l:
                    if(j in dict):
                        d[files[0]] = j
                        break;
    print("有唯一字符串的类有"+str(len(d)))
    return d
result = {}
def find_new(dict,set):
    for key in dict:
        files = glob.glob(new_dir+"/"+"smali*/*/"+"*.smali",recursive=True)
        for file in files:
            with open(file, 'r') as f:
                if(dict[key] in f.read()):
                    result[get_type(key)] = get_type(file)
                    parse_smali(key,file,set)
                    break;
def get_type(str):
    str = str.split('/')[-1]
    str = str.split('.')[0]
    return str

def parse_smali(old_file,new_file,set):
    print(old_file)
    print(new_file)
    dict = {}
    with open(old_file, 'r') as f:
        list = Statement.parse_lines(f.read())
        for item in list:
            if(isinstance(item,FieldStatement)):
                if(item.type_descriptor in set):
                    dict[item.member_name] = item.type_descriptor
    with open(new_file, 'r') as f:
        list = Statement.parse_lines(f.read())
     
        for item in list:
            if(isinstance(item,FieldStatement)):
                if(item.member_name in dict):
                    print(item.member_name+"->"+item.type_descriptor)
                    result[dict[item.member_name]] = item.type_descriptor

if __name__ == "__main__":
    dict = search_string()
    # set = search_lx()
    # dict = x_s(set,dict)
    # find_new(dict,set)
    # print("对应关系个数："+str(len(result)))
    # print(result)
    
