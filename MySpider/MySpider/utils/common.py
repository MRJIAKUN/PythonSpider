# _*_coding:utf-8 _*_
__author__ = 'david'
__date__ = '2018/5/26 22:58'
import hashlib
import datetime
import re

# 将 url转化为md5
def get_md5(url):
    if isinstance(url, str):
        url= url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

# 将string类型的时间转化为date类型
def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

