"""
使用该脚本进行登录
登录后会保存相应的cookie信息到 cookies.txt
"""
import time
import json
from selenium import webdriver

options = webdriver.ChromeOptions()
options.binary_location = "chrome-win64/chrome.exe"
driver = webdriver.Chrome(options=options, executable_path='webdriver/chromedriver.exe')
# 自行替换下边的域名为你可以访问的
driver.get('https://sjs47.me/home.php?mod=space')

# 20秒后自动保存，请在20秒内登录操作完成, 觉得不够还可以修改延长
time.sleep(20)
with open('cookies.txt','w') as f:
    # 将cookies保存为json格式
    f.write(json.dumps(driver.get_cookies()))
driver.quit()