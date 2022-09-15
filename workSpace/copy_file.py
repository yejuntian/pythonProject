import argparse
import os

def copy(from_dir,to_dir):
    from_res_dir = from_dir+"/res"
    to_res_dir = to_dir+"/res"
    #获取res文件夹下所有文件夹
    for dir in os.listdir(from_res_dir):
        from_child_dir = from_res_dir+"/"+dir
        to_child_dir = to_res_dir+"/"+dir
        #如果不存在文件夹
        if(not os.path.isdir(to_child_dir)):
            print("创建文件夹"+to_child_dir)
            os.system('mkdir {dir}'.format(dir=to_child_dir))
        #列出文件夹下所有文件
        list = os.listdir(to_child_dir)
        for file in os.listdir(from_child_dir):
            #如果文件不存在
            if(file not in list):
                print(from_child_dir+"/"+file)
                cp = 'cp {from_dir}/{file} {to_dir}'.format(from_dir=from_child_dir,file=file,to_dir=to_child_dir).replace("$", "\$")
                os.system(cp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    options = parser.parse_args()
    copy(options.from_dir,options.to_dir)