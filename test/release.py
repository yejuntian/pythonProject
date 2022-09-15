import argparse
import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse
from datetime import datetime

import requests

version_name = "2.22.10.55_test"
version_code = "2139210155"
type="gb"
name="GB逆向"
# 更新说明
update = """
1. 添加静默安装功能
2. 添加信息流广告
3. 修复广告不能点击的bug
"""


output = "OutputApk/GB"
decode = "DecodeCode/GBWhatsApp_v17"
unalign = output+"/GBWhatsApp_unalign.apk"
unsign = output+"/GBWhatsApp_unsign.apk"
key = "key/gbwhatsapp.jks"
now = datetime.strftime(datetime.now(), "%m_%d_%H%M")
apk = output+"/GBWhatsApp_"+version_name+"_"+now+".apk"

headers = {"Accept": "application/vnd.github.v3+json",
           "Authorization": "token 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"}
# 修改apktool.yml的版本
def change_version():
    os.system('rm -rf '+output)
    os.system('rm -rf '+decode+"/build")
    result = ""
    print(">>>> change version <<<<")
    with open(decode+"/apktool.yml", 'r') as f:
        lines = f.readlines()
        for line in lines[:-2]:
            result += line
        result += "  versionCode: '{version_code}'\n".format(
            version_code=version_code)
        result += "  versionName: "+version_name
    with open(decode+"/apktool.yml", "w") as f:
        f.write(result)




def build_apk():
    print(">>>> building apk <<<<")
    os.system(
        'apktool b -o {unalign} {decode}'.format(unalign=unalign, decode=decode))
    print(">>>> aligning apk <<<<")
    os.system(
        'zipalign -f 4 {unalign} {unsign}'.format(unalign=unalign, unsign=unsign))
    print(">>>> signing apk <<<<")
    os.system('apksigner sign --ks {key} --ks-pass pass:gbwhatsapp --out {apk} {unsign}'.format(
        key=key, apk=apk, unsign=unsign))


def build_web():
    print(datetime.now())
    file = "https://raw.githubusercontent.com/qweruqwio/apk/master/"+apk
    content = {
        "version":version_name,
        "url":file,
        "type":type,
        "name":name,
        "date":datetime.now().strftime("%Y-%m-%d %H时%M分%S秒")
    }
    print(json.dumps(content))
    body = {"ref": "master",
            "inputs": {
                "content": json.dumps(content)
            }
            }
    h = {"Accept": "application/vnd.github.v3+json",
         "Authorization": "token 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"}
    r = requests.post(
        "https://api.github.com/repos/malinkang/gbwhatsapp/actions/workflows/29505793/dispatches",
        headers=h,
        json=body
    )
    print(r.status_code)


def upload_to_github():
    print(">>>> start upload <<<<")
    with open(apk, "rb") as file:
        base64_bytes = base64.b64encode(file.read())
        content = base64_bytes.decode("ascii")
    body = {"message": "上传apk", "content": content}
    r = requests.put(
        "https://api.github.com/repos/qweruqwio/apk/contents/"+apk,
        headers=headers,
        json=body,
    )
    print(r.status_code)
    print(r.text)
    if(r.status_code == 200 or r.status_code==201):
        print(">>>> upload success <<<<")
        print(datetime.now())
        send_to_dingding()
    else:
        #上传失败再次上传
        upload_to_github()
#
def send_to_dingding():
    md5 = hashlib.md5(open(apk,'rb').read()).hexdigest()
    print(md5)
    print(">>>> send to dingding <<<<")
    url = "https://gbwhatsapp.malinkang.com/"
    content = "应用名称：{name}\n下载地址：{url}\n更新说明：\n{update}\nMD5:{md5}\n版本号：{version_name}".format(name=name,url=url,update=update.strip(), md5=md5,version_name=version_name)
    atMobiles = []
    atMobiles.append("18611145755") # 马林康
    atMobiles.append("18610828434") # 王闯
    atMobiles.append("13853793201") # 王熳
    atMobiles.append("13263660627") # 项筠清
    atMobiles.append("18812165098") # 王彭莹
    content = content.format(url=url, update=update)
    print(content)
    timestamp = str(round(time.time() * 1000))
    secret = 'SEC8a35ae010c216f6e26418c5fa2693e78d73c00a202f47b4079f5fe3cbf0ec32f'
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc,
                         digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = 'https://oapi.dingtalk.com/robot/send?access_token=b4b8650e4206aef4bd0a46eef565001ef1d98efdb284b54898e4cdecffba0b71&timestamp='+timestamp+'&sign='+sign
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    body = {"msgtype": "text", "text": {"content": content},
            "at": {"atMobiles": atMobiles}, "isAtAll": False}
    print(body)
    r = requests.post(url, headers=headers, data=json.dumps(body))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    build_web()
    change_version()
    build_apk()
    upload_to_github()


