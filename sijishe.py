# -*- coding: utf8 -*-

"""
cron: 0 8 * * *
new Env('司机社签到');
环境变量名称：XSIJISHE
直接使用账号密码登录,格式: 账号&密码
多个账号使用@间隔
青龙Python依赖, requests, lxml
[task_local]
#司机社签到
0 8 * * * https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/sijishe.py, tag=司机社签到, enabled=true
[rewrite_local]
https://sijishea.com url script-request-header https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/sijishe.py
"""

import os
from lxml import etree
import time
from sendNotify import send
import urllib3
import re
import hashlib
import requests
import random

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
def string_to_md5(key):
    md5 = hashlib.md5()
    md5.update(key.encode("utf-8"))
    return md5.hexdigest()

def getrandom(code_len):
    all_char = 'qazwsxedcrfvtgbyhnujmikolpQAZWSXEDCRFVTGBYHNUJIKOLP'
    index = len(all_char) - 1
    code = ''
    for _ in range(code_len):
        num = random.randint(0, index)
        code += all_char[num]
    return code


# 从发布页获取网站地址
def get_new_url():
    global main_url
    url = 'https://sijishe.me/'
    try:
        res = requests.get(url)
        rhtml = etree.HTML(res.text)
        urls = rhtml.xpath('//*[@id="main"]/div/div[2]/div/div/a[1]/@href')[0]
        main_url = str(urls)
        # print(main_url)
        return 1
    except:
        print('发布页地址获取失败，请检查网络连接')
    exit(0)

# 初始化cookie和页面formhash信息
def get_cookie_formhash():
    global formhash
    formhash = ''
    response = requests.get(main_url + '/member.php?mod=logging&action=login&frommessage')
    # response.cookies 返回为cookiejar，需转成json方便使用
    cookiejar_to_json(response.cookies)
    # print(cookies)
    formhash = re.findall(r'<input type="hidden" name="formhash" value="(.*)" />', response.text)[0]
    # print(formhash[0])

# cookiejar转为json
def cookiejar_to_json(Rcookie):
    global cookies
    for item in Rcookie:
        cookies[item.name] = item.value

def login(username, password):
    data = {
        'formhash': formhash,
        'referer': main_url + '/home.php?mod=space&do=pm&filter=newpm',
        'username': username,
        'password': password,
        'questionid': '0',
        'answer': '',
    }

    login_url = main_url + '/member.php?mod=logging&action=login&loginsubmit=yes&frommessage&loginhash=Lt' + getrandom(3) + '&inajax=1'
    try:
        response = requests.post(login_url, cookies=cookies, headers=headers, data=data)
        cookiejar_to_json(response.cookies)
        response.text.index('欢迎您回来')
        # print('登录成功')
        # print(cookies)
        return 1
    except:
        print(f'账号{username}登录失败，请检查账号密码, 可能是验证码问题，等待更新...')
        return 0

def start(postdata):

    # 账号数据按格式分割
    global send_content
    try:
        payload = postdata.split('@')
        print('发现', len(payload), '个账号信息\n')
        send_content += f'发现 {len(payload)} 个账号信息\n'
        # info = '发现 ' + str(len(payload)) + ' 个账号信息\n\n'
    except:
        print('环境变量格式错误, 程序退出')
        print(e)
        exit(0)
    global checkIn_status

    for i in payload:
        try:
            u = i.split('&')
            # 读取账号到变量，密码为md5编码后的字符串
            name = u[0]
            pwd = string_to_md5(u[1])
        except:
            print('账号参数格式错误')
            break

        # 刷新cookie和formhash值，用作登录
        get_cookie_formhash()
        if not login(name, pwd):
            send_content += f'账号{name}登录失败,请检查账号密码\n\n'
            continue
        headers = {
            'referer': main_url + '/',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39'
        }
        s = requests.session()
        #s.proxies = {'https': '101.200.127.149:3129', }

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
            s.get(main_url+ '/' + qiandao_url, cookies=cookies, headers=headers, timeout=30, verify=False)
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
    #s.proxies = {"https": "101.200.127.149:3129"}

    try:
        res = s.request("GET", main_url + sign_url, cookies=cookies, headers=headers, timeout=30, verify=False)
        # print(res.text)
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
        res = s.request("GET", main_url + '/home.php?mod=space', cookies=cookies, headers=headers, timeout=30, verify=False)
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
        print('访问用户信息失败，可能存在网络波动')
        print(e)
    #exit(0)
    # 格式化输出内容并居中
    xm = "账户【" + xm +"】"
    xm = xm.center(24, '=')

    print(xm)
    print(f'签到状态: {checkIn_content[checkIn_status]} \n{lxqiandao_content} \n当前积分: {jf[0]}\n当前威望: {ww[0]}\n当前车票: {cp[0]}\n当前贡献: {gx[0]}\n\n')
    # exit(0)
    global send_content
    send_content += f'{xm}\n签到状态: {checkIn_content[checkIn_status]} \n{lxqiandao_content} \n当前积分: {jf[0]}\n当前威望: {ww[0]}\n当前车票: {cp[0]}\n当前贡献: {gx[0]}\n\n'

# 阿里云函数入口
def handler(event, context):
    try:
        _postdata = os.environ['XSIJISHE']
    except Exception:
        print('未设置环境变量 XSIJISHE')
        exit(0)
    if get_new_url():
        start(_postdata)
    exit(0)


if __name__ == '__main__':
    handler('', '')
