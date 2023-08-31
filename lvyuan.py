"""
抓包地址：vip.luyuan.cn/huiyuan/userbike/list
多个账号使用@或者换行间隔
青龙Python依赖, requests, urllib3, os, re, json
[task_local]
#绿源电动车签到
0 8,22 * * * https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/lvyuan.py, tag=绿源电动车签到, enabled=true
"""

import json
import os
import re

import requests
import urllib3

from sendNotify import send

urllib3.disable_warnings()
send_content = ''

def start(ck):
    global send_content
    try:
        payload = re.split('@|\n', ck)
        print('发现', len(payload), '个账号信息\n')
        send_content += f'发现 {len(payload)} 个账号信息\n\n'
    except Exception as e:
        print(e)
        print('环境变量格式错误, 程序退出')
        exit(0)

    for i in payload:
        authorization = i
        # api_sign = re.split(',', i)[1]
        check_in(authorization)

    send('绿源电动车签到', send_content)


def check_in(authorization):
    global send_content
    headers = {
        'Host': 'vip.luyuan.cn',
        'Connection': 'keep-alive',
        'authorization': authorization,
        'charset': 'utf-8',
        # 'api-key': api_key,
        # 'api-sign': api_sign,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; HD1900 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5235 MMWEBSDK/20230303 MMWEBID/3666 MicroMessenger/8.0.34.2340(0x28002237) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'Referer': 'https://servicewechat.com/wx7a47c4837513ee24/143/page-frame.html',
    }
    postdata = {}
    # 获取昵称
    name = ''
    try:
        res = requests.get('https://vip.luyuan.cn/huiyuan/user/userprofile/fetch', headers=headers, verify=False)
        resjson = json.loads(res.text)
        if resjson['ok'] == True:
            name = resjson['data']['nickname']
    except Exception as e:
        print('get name', e)

    # 签到
    try:
        res = requests.post('https://vip.luyuan.cn/huiyuan/usertask/user/sign/in', headers=headers, data=postdata,
                            verify=False)
        resjson = json.loads(res.text)
        if resjson['ok'] == True:
            print(f'{name} 签到成功')
            send_content += f'{name} 签到成功\n'
        elif resjson['ok'] == False:
            print(f'{name} 已经签到')
            send_content += f'{name} 已经签到\n'
    except Exception as e:
        print(e)

    # 获取总积分
    try:
        res = requests.get('https://vip.luyuan.cn/huiyuan/user/fetch', headers=headers, verify=False)
        resjson = json.loads(res.text)
        if resjson['ok'] == True:
            totalpoints = resjson['data']['totalpoints']
            print(f'当前总积分: {totalpoints}')
            send_content += f'当前总积分: {totalpoints}\n\n'
    except Exception as e:
        print('get totalpoints', e)


# 阿里云函数入口
def handler(event, context):
    try:
        _postdata = os.environ['LVYUAN_CK']
    except Exception:
        print('未设置环境变量 LVYUAN_CK')
        exit(0)
    start(_postdata)
    exit(0)


if __name__ == '__main__':
    handler('', '')
