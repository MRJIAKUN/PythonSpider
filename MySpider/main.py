# _*_coding:utf-8 _*_
__author__ = 'david'
__date__ = '2018/5/25 20:47'

from scrapy.cmdline import execute

import sys
import os

# 获取文件目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 启动spider命令
execute(["scrapy", "crawl", "zhihu_selenium"])
# execute(["scrapy", "crawl", "jobbole"])