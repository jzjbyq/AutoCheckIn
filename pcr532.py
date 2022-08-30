# -*- coding: utf8 -*-

"""
cron: 12 8 * * *
new Env('pcr532签到');
环境变量名称：PCR532_QD
账号密码使用 user&pwd 格式，多个账号使用@间隔
"""
import requests
import os
import base64
import time
import re
from sendNotify import send
import urllib3

urllib3.disable_warnings()

def start(postdata):

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    info = ''
    name = ''
    pwd = ''
    glod = 0
    #账号数据按格式分割
    try:
        payload = postdata.split('@')
        print('检测到', len(payload), '个账号信息\n')
        #info = '发现 ' + str(len(payload)) + ' 个账号信息\n\n'
    except:
        print('环境变量格式错误, 程序退出')
        exit(0)

    #循环每个账号信息进行签到
    for index, i in enumerate(payload):
        try:
            u = i.split('&')
            # 提交内容格式化，密码为base64编码后的字符串
            name = u[0]
            pwd = base64.b64encode(u[1].encode()).decode('utf8')
            p = 'username=' + name + '&passc=' + pwd
        except:
            print('账号参数格式错误')
            break
        try:
            user = name.replace(name[3:-4], '*'*len(name[3:-4]))
            response = requests.request("POST", 'https://www.rfidfans.com/upload/qiandao.php', headers=headers, data=p, verify=False, timeout=30)
            days = re.findall(r"连续(.*)天打卡", response.text)[0]
            golds = re.findall(r"奖励(\d+)个金币(.*)", response.text)[0][0]
            glod = get_glod(name, pwd)
            # info += f'账号 {user} 第{str(days)}天签到, 获得{str(golds)}个金币\n'
            info += f'==========账号 {index + 1}==========\n账　　号：{user}\n签到状态：签到成功\n签到天数：{days}\n获得金币：{golds}\n金币总数：{glod}\n\n'
            print(f'==========账号 {index + 1}==========\n账　　号：{user}\n签到状态：签到成功\n签到天数：{days}\n获得金币：{golds}\n金币总数：{glod}\n\n')
        except:
            try:
                if response.text.index('今天已经签过了'):
                    info += f'账号 {user} 今天已签到\n'
                    print(f'账号 {user} 今天已签到')
            except:
                info += f'账号 {user} 签到失败\n'
                print(f'账号 {user} 签到失败')
        # 间隔3秒，防止提交过快
        time.sleep(3)

    send("Pcr532签到结果", '\n' + info)

def get_glod(name, pwd):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'host': 'www.rfidfans.com'
    }
    p = 'passB=cG41MzJjYXJkcmVhZGVy&passA=cHJpdmF0ZWluZm8=&username=' + name + '&passc=' + pwd
    try:
        res = requests.request("POST", 'https://www.rfidfans.com/upload/info_search.php', headers=headers, data=p, verify=False, timeout=30).json()
        return int(res[0]["jinbi"])
    except:
        pass
    return 0
if __name__ == '__main__':
    try:
        _postdata = os.environ['PCR532_QD']
    except Exception:
        print('未设置环境变量 PCR532_QD')
        exit(0)
    start(_postdata)