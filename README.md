# AutoCheckIn

### 自用签到集合

####本项目中的脚本推荐在青龙中使用，也兼容在阿里云函数运行

1、pcr532App签到 第一天1积分，第二天2积分，依次增加，上限是7 \
可兑换积分商城里的所有东西 \
有需要的 可自行到 https://www.rfidfans.com/ 下载APP注册

2、sijishe签到 LSP都懂，脚本可自动从sijishe.me获取最新地址进行账号登录、签到 \
嗯，资源很贵，车票很重要

3、增加老王部落签到，可获取签到积分奖励，每7天一轮每日奖励



sijishe由20240717开始只支持docker版青龙，其它方式请自行研究使用

sijishe网站做了加密，由于不懂js，索性直接换selenium方式来搞定，关于青龙面板
安装selenium和对应的chromiumdriver安装方式，看下边的说明吧

青龙面板中可以直接安装 selenium 依赖

安装chromium, 先进入到docker青龙的控制台中

```
docker exec -it qinglong bash
```

按照下边步骤进行安装
1、切换国内镜像源

```
sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
```

2、安装chromium以及chromiumdriver

```
apk add chromium
apk add chromium-chromedriver
```

3、使用 python代码 测试是否安装成功，以上安装没问题，可以不用测试

```
# -*-coding: utf-8 -*-
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.baidu.com')
print(driver.title)
```

sijishe_login.py 用到的组件 https://jzjbyq.lanzouo.com/ilFmi24pabha
