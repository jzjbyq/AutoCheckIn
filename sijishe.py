# -*- coding: utf8 -*-

"""
cron: 0 8 * * *
new Env('司机社签到');
环境变量名称：XSIJISHE_CK
可以使用浏览器抓包, 打开签到页面 找到两个Key SgL6_2132_saltkey=xxxxxx; SgL6_2132_auth=xxxxxx;
多个账号使用@间隔
青龙Python依赖, requests, lxml
"""

import requests
import os
from lxml import etree
import time
from sendNotify import send
import urllib3

urllib3.disable_warnings()

# 初始化签到状态值
checkIn_content = '今日已签到', '签到成功', 'Cookie失效'
checkIn_status = 2
send_content = ''

def start(postdata):
    # 签到积分信息页面
    url = 'https://xsijishe.net/k_misign-sign.html'

    # 账号数据按格式分割
    global send_content
    try:
        payload = postdata.split('@')
        print('发现', len(payload), '个账号信息\n')
        send_content += f'发现 {len(payload)} 个账号信息\n'
        # info = '发现 ' + str(len(payload)) + ' 个账号信息\n\n'
    except:
        print('环境变量格式错误, 程序退出')
        exit(0)

    global checkIn_status

    for i in payload:
        headers = {
            'cookie': i,
            'referer': 'https://xsijishe.net/',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39'
        }
        s = requests.session()
        #s.proxies = {'https': '101.200.127.149:3129', }
        res = s.request("GET", url, headers=headers, timeout=30, verify=False)
        # print(res.text)
        rhtml = etree.HTML(res.text)

        # 获取签到信息
        get_url = rhtml.xpath('//*[@id="JD_sign"]/@href')
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
            qiandao_url = 'https://xsijishe.net/' + get_url[0]
            qiandao_url.index('operation=qiandao')
        except:
            #print('今日已签到')
            checkIn_status = 0
            printUserInfo(i, lxqiandao_content)
            continue

        try:
            s.request('GET', qiandao_url, headers=headers, timeout=30, verify=False)
            #print('签到成功')
            checkIn_status = 1
        except:
            print('Cookie失效')
        printUserInfo(i, lxqiandao_content)

    send('司机社签到', send_content)

# 获取用户积分信息
def printUserInfo(uinfo, qiandao_content):

    headers = {
        'cookie': uinfo,
        'referer': 'https://xsijishe.net/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77'
    }
    s = requests.session()
    # 关闭多余连接
    s.keep_alive = False
    # 使用代理服务
    #s.proxies = {"https": "101.200.127.149:3129"}
    try:
        res = s.request("GET", 'https://xsijishe.net/home.php?mod=space', headers=headers, timeout=30, verify=False)
        time.sleep(1)
        #print(res.text)
        #print(res.status_code)
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
        print('访问用户信息失败')
        print(e)
    #exit(0)

    print(f'=============账户【{xm}】=============')
    print(f'签到状态: {checkIn_content[checkIn_status]} \n{qiandao_content} \n当前积分: {jf[0]}\n当前威望: {ww[0]}\n当前车票: {cp[0]}\n当前贡献: {gx[0]}')
    # exit(0)
    global send_content
    send_content += f'=============账户【{xm}】=============\n签到状态: {checkIn_content[checkIn_status]} \n{qiandao_content} \n当前积分: {jf[0]}\n当前威望: {ww[0]}\n当前车票: {cp[0]}\n当前贡献: {gx[0]}\n\n'


if __name__ == '__main__':
    try:
        _postdata = os.environ['XSIJISHE_CK']
    except Exception:
        print('未设置环境变量 XSIJISHE_CK')
        exit(0)

start(_postdata)
