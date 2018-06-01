# _*_coding:utf-8 _*_
__author__ = 'david'
__date__ = '2018/5/28 15:08'

'''
使用requests方法模拟知乎登录
'''
import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")

try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0"
header = {
    "HOST":"www.zhihu.com",
    "Referer":"https://www.zhihu.com/",
    "User-Agent":agent
}

# 获取xsrf
def get_xsrf():
    response = session.get("https://www.zhihu.com/", headers=header)
    # 用正则表达式取出xsrf
    match_obj = re.match('.* name="_xsrf" value="(.*?)"', response.text.encode("utf-8"))
    if match_obj:
        return (match_obj.group(1))
    else:
        return ""

def get_captcha():
    import time
    t = str(int(time.time()*1000))
    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
    t = session.get(captcha_url, headers=header)
    with open("captcha.jpg","wb") as f:
        f.write(t.content)
        f.close()

    from PIL import Image
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass

    captcha = input("输入验证码\n>")
    return captcha


def get_index():
    response = session.get("https://www.zhihu.com/", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text)
    print("OK")

# 判断用户是否已登录
def is_login():
    inbox_url ="https://www.zhihu.com/inbox"
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True

def zhihu_login(account, password):
    if re.match("^1\d{10}", account):
        print("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf":get_xsrf(),
            "phone_num": account,
            "password": password,
            "captcha": get_captcha()
        }


    else:
        if "@" in account:
            print("邮箱登录")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password
            }
    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()

# zhihu_login("13144485182","CAISIYUAN")
# get_index()