# -*- coding: utf8 -*-
"""
cron: 0 8 * * *
new Env('司机社签到');
环境变量名称：XSIJISHE
XSIJISHE: 存储登录的cookie信息, 使用 sijishe_login.py 进行登录后生成的 cookies.txt，将文件内容存到变量中
多个账号在XSIJISHE变量中使用@或换行间隔
青龙Python依赖, requests, lxml, selenium, msedge-selenium-tools
[task_local]
#司机社签到
0 8 * * * https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/sijishe.py, tag=司机社签到, enabled=true
[rewrite_local]
https://sijishea.com url script-request-header https://raw.githubusercontent.com/jzjbyq/AutoCheckIn/main/sijishe.py
"""
import os
import re
import time
import json
from lxml import etree

from sendNotify import send

# 初始化签到状态值
checkIn_content = '今日已签到', '签到成功', 'Cookie失效'
checkIn_status = 2
send_content = ''
cookies = ''

# 签到积分信息页面
sign_url = '/k_misign-sign.html'
home_url = '/home.php?mod=space'

main_url = ''

# 初始化浏览器信息
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
# 设置无界面模式，也可以添加其它设置
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

def start(postdata):
    # 账号数据按格式分割
    global send_content
    global main_url
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
        cookies = json.loads(i)
        # 获取登录页面地址
        main_url = f"https://{cookies[0]['domain']}"
        
        # 获取签到地址
        try:
            res = get_page_source(main_url + home_url, cookies)
            rhtml = etree.HTML(res)
            # cookiejar_to_json(res.cookies)
            # print(res.text)
            qiandao_url = rhtml.xpath('//*[@id="JD_sign"]/@href')[0]
            # print(qiandao_url)
        except:
            # print('今日已签到')
            checkIn_status = 0

        try:
            get_page_source(main_url + '/' + qiandao_url, cookies)
            print('签到成功')
            checkIn_status = 1
        except Exception as e:
            # print(e)
            checkIn_status = 0
        printUserInfo()

    send('司机社签到', send_content)


# 获取用户积分信息
def printUserInfo():
    try:
        res = get_page_source(main_url + sign_url, cookies)
        rhtml = etree.HTML(res)
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
        res = get_page_source(main_url + home_url, cookies)
        rhtml = etree.HTML(res)
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

def get_page_source(web_url, cookies):
    time.sleep(3)
    driver.get(web_url)
    driver.delete_all_cookies()
    # cookies_list = json.loads(cookies)
    cookies_list = cookies
    # 方法1 将expiry类型变为int
    for cookie in cookies_list:
        # 并不是所有cookie都含有expiry 所以要用dict的get方法来获取
        if isinstance(cookie.get('expiry'), float):
            cookie['expiry'] = int(cookie['expiry'])
        driver.add_cookie(cookie)
    driver.refresh()
    source = driver.page_source
    time.sleep(3)
    return source

# 阿里云函数入口
def handler(event, context):
    try:
        _postdata = os.environ['XSIJISHE']
    except Exception:
        print('未设置正确的环境变量 XSIJISHE')
        exit(0)
    start(_postdata)
    driver.quit()
    exit(0)


if __name__ == '__main__':
    handler('', '')