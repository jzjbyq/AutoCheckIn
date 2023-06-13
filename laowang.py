# -*- coding: utf8 -*-

"""
cron: 0 8 * * *
new Env('老王资源部落签到');
环境变量名称：LAOWANG_CK
cookie抓包 wordpress_sec_xxxxxxxxxx 即可
多个账号使用@或者换行间隔
青龙Python依赖, requests, lxml
[task_local]
#老王资源部落签到
0 8 * * * https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/laowangziyuan.py, tag=老王资源部落签到, enabled=true
[rewrite_local]
https://www.laowang2021.com url script-request-header https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/laowangziyuan.py
"""

import re
import os
import requests
import urllib3
from sendNotify import send
from lxml import etree

urllib3.disable_warnings()
send_content = ''


def start(ck):
    global send_content
    try:
        payload = re.split('@|\n', ck)
        print('发现', len(payload), '个账号信息\n')
        send_content += f'发现 {len(payload)} 个账号信息\n'
    except Exception as e:
        print(e)
        print('环境变量格式错误, 程序退出')
        exit(0)
    for i in payload:
        name = re.findall('.*\=(.*?)[\%\|]', i)[0]
        headers = {
            'authority': 'www.laowang2021.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': i,
            'origin': 'https://www.laowang2021.com',
            'pragma': 'no-cache',
            'referer': 'https://www.laowang2021.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42',
            'x-requested-with': 'XMLHttpRequest',
        }
        # 开始签到
        data = {
            'action': 'user_checkin',
        }
        # {'msg': '连续4天签到成功！ 积分+20 经验值+5', 'data': {'integral': 5, 'points': 20, 'time': '2022-11-18 15:51:55'}, 'continuous_day': 4, 'details_link': '<a data-class="modal-mini" mobile-bottom="true" data-height="240" data-remote="https://www.laowang2021.com/wp-admin/admin-ajax.php?action=checkin_details_modal" class=" checkin-details-link" href="javascript:;" data-toggle="RefreshModal"></a>', 'error': False}
        res = requests.post('https://www.laowang2021.com/wp-admin/admin-ajax.php', headers=headers,
                            data=data).json()
        if res == 0:
            print(name, '的Cookie已过期')
            send_content += f'{name} 的Cookie已过期\n'
            continue
        msg = res['msg']

        # 获取签到天数
        params = {
            'action': 'checkin_details_modal',
        }
        try:
            res = requests.get('https://www.laowang2021.com/wp-admin/admin-ajax.php', params=params, headers=headers)
            qday = re.findall(r'<badge class="c-blue">(.*)</badge>', res.text)[0]
            # print(qday)
        except:
            qday = '未知'

        # 获取当前积分数
        try:
            res = requests.get('https://www.laowang2021.com/user/balance', headers=headers)
            rhtml = etree.HTML(res.text)
            integral = rhtml.xpath('//*[@id="user-tab-balance"]/div[1]/div[1]/div/div/div[2]/div[1]/span/text()')[0]
        except Exception as e:
            print(e)

        xm = "账户【" + name + "】"
        xm = xm.center(24, '=')
        print(
            f'{xm}\n签到状态: {msg} \n当前积分: {integral}\n累计签到：{qday}天\n\n')
        send_content += f'{xm}\n签到状态: {msg} \n当前积分: {integral}\n累计签到：{qday}天\n\n'

    send('老王资源部落签到', send_content)


# 阿里云函数入口s
def handler(event, context):
    try:
        _postdata = os.environ['LAOWANG_CK']
    except Exception:
        print('未设置环境变量 LAOWANG_CK')
        exit(0)
    start(_postdata)
    exit(0)


if __name__ == '__main__':
    handler('', '')
