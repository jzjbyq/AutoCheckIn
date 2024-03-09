# -*- coding: utf8 -*-

"""
cron: 0 8 * * *
new Env('司机社签到');
环境变量名称：XSIJISHE, XSIJISHE_URL
没有实现idhash的获取，所以需要登录后抓取cookie, 和设置你网络可以打开的网页地址
cookie需要的键值：SgL6_2132_saltkey, SgL6_2132_auth
变量中cookie格式(第二个键值后边不用分号): SgL6_2132_saltkey=xxxxxxxx; SgL6_2132_auth=xxxxxxx
多个账号使用@或换行间隔
青龙Python依赖, requests, lxml
[task_local]
#司机社签到
0 8 * * * https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/sijishe.py, tag=司机社签到, enabled=true
[rewrite_local]
https://sijishea.com url script-request-header https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/sijishe.py
"""

import os
import re
import time

import requests
import urllib3
from lxml import etree

from sendNotify import send

urllib3.disable_warnings()

# 初始化签到状态值
checkIn_content = '今日已签到', '签到成功', 'Cookie失效'
checkIn_status = 2
send_content = ''
cookies = {}

# 签到积分信息页面
sign_url = '/k_misign-sign.html'

formhash = ''
main_url = ''
headers = {}


def start(postdata):
    # 账号数据按格式分割
    global send_content
    try:
        payload = re.split('@|\n', postdata)
        print('发现', len(payload), '个账号信息\n')
        send_content += f'发现 {len(payload)} 个账号信息\n'
        # info = '发现 ' + str(len(payload)) + ' 个账号信息\n\n'
    except:
        print('环境变量格式错误, 程序退出')
        print(e)
        exit(0)
    global checkIn_status
    global cookies
    for i in payload:
        try:
            data = i
        except:
            print('账号参数格式错误')
            break
        for item in data.split(";"):
            key, value = item.strip().split("=")
            cookies[key] = value
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        }
        s = requests.session()
        # s.proxies = {'https': '101.200.127.149:3129', }

        # 获取签到地址
        try:
            res = s.get(main_url + '/k_misign-sign.html', cookies=cookies, headers=headers, timeout=30)
            rhtml = etree.HTML(res.text)
            # cookiejar_to_json(res.cookies)
            # print(res.text)
            qiandao_url = rhtml.xpath('//*[@id="JD_sign"]/@href')[0]
            # print(qiandao_url)
        except:
            # print('今日已签到')
            checkIn_status = 0

        try:
            s.get(main_url + '/' + qiandao_url, cookies=cookies, headers=headers, timeout=30, verify=False)
            # print('签到成功')
            checkIn_status = 1
        except Exception as e:
            # print(e)
            checkIn_status = 0
        printUserInfo()

    send('司机社签到', send_content)


# 获取用户积分信息
def printUserInfo():
    headers = {
        'referer': main_url + '/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77'
    }
    s = requests.session()
    # 关闭多余连接
    s.keep_alive = False
    # 使用代理服务
    # s.proxies = {"https": "101.200.127.149:3129"}

    try:
        res = s.request("GET", main_url + sign_url, cookies=cookies, headers=headers, timeout=30, verify=False)
        rhtml = etree.HTML(res.text)
    except Exception as e:
        print('访问用户信息失败，Cookie失效')
        print(e)
    # 签到排名
    qiandao_num = rhtml.xpath('//*[@id="qiandaobtnnum"]/@value')[0]
    # 连续签到天数
    lxdays = rhtml.xpath('//*[@id="lxdays"]/@value')[0]
    # 总签到天数
    lxtdays = rhtml.xpath('//*[@id="lxtdays"]/@value')[0]
    # 签到等级
    lxlevel = rhtml.xpath('//*[@id="lxlevel"]/@value')[0]
    # 签到获取车票奖励数
    lxreward = rhtml.xpath('//*[@id="lxreward"]/@value')[0]
    # 格式化签到信息内容
    lxqiandao_content = f'签到排名：{qiandao_num}\n签到等级：Lv.{lxlevel}\n连续签到：{lxdays} 天\n签到总数：{lxtdays} 天\n签到奖励：{lxreward}\n'

    try:
        res = s.request("GET", main_url + '/home.php?mod=space', cookies=cookies, headers=headers, timeout=30,
                        verify=False)
        time.sleep(1)
        # print(res.text)
        # print(res.status_code)
        rhtml = etree.HTML(res.text)
        # 账户名称
        xm = rhtml.xpath('//*[@id="ct"]/div/div[2]/div/div[1]/div[1]/h2[1]/text()')[0].replace("\r\n", "")
        # 当前车票数
        cp = rhtml.xpath('//*[@id="psts"]/ul/li[4]/text()')
        # 当前积分
        jf = rhtml.xpath('//*[@id="psts"]/ul/li[2]/text()')
        # 当前威望
        ww = rhtml.xpath('//*[@id="psts"]/ul/li[3]/text()')
        # 当前贡献
        gx = rhtml.xpath('//*[@id="psts"]/ul/li[5]/text()')
    except Exception as e:
        print('访问用户信息失败，可能存在网络波动')
        print(e)
    # exit(0)
    # 格式化输出内容并居中
    xm = "账户【" + xm + "】"
    xm = xm.center(24, '=')

    print(xm)
    print(
        f'签到状态: {checkIn_content[checkIn_status]} \n{lxqiandao_content} \n当前积分: {jf[0]}\n当前威望: {ww[0]}\n当前车票: {cp[0]}\n当前贡献: {gx[0]}\n\n')
    # exit(0)
    global send_content
    send_content += f'{xm}\n签到状态: {checkIn_content[checkIn_status]} \n{lxqiandao_content} \n当前积分: {jf[0]}\n当前威望: {ww[0]}\n当前车票: {cp[0]}\n当前贡献: {gx[0]}\n\n'


# 阿里云函数入口
def handler(event, context):
    global main_url
    try:
        _postdata = os.environ['XSIJISHE']
        main_url = os.environ['XSIJISHE_URL']
    except Exception:
        print('未设置正确的环境变量 XSIJISHE, XSIJISHE_URL')
        exit(0)
    start(_postdata)
    exit(0)


if __name__ == '__main__':
    handler('', '')