# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst,Join

from settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
from utils.common import date_convert,get_nums,get_md5

import MySQLdb
import MySQLdb.cursors

def remove_comment_tags(value):
    # 去掉tag提取的评论
    if "评论" in value:
        return ""
    else:
        return value

def return_value(value):
    return value

class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobBoleArticleItem(scrapy.Item):

    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        output_processor = Join(",")
    )
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """
                            insert into jobbole_article(title, create_date, url, url_object_id, front_image_url, front_image_path, comment_nums, praise_nums, fav_nums, tags, content)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE comment_nums=VALUES(comment_nums), fav_nums=VALUES(fav_nums)
                        """
        params = (self["title"], self["create_date"], self["url"], self["url_object_id"], self["front_image_url"],
                  self["front_image_path"], self["comment_nums"], self["praise_nums"], self["fav_nums"], self["tags"],
                  self["content"])

        return insert_sql, params


# 自定义itemloader
class ArticleItemLoader(ItemLoader):
    # 取出list中的第一个值
    default_output_processor = TakeFirst()



class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field(
        input_processor=Join(",")
    )
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comments_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    watch_user_num =scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(",","").strip())
            click_num = int(self["watch_user_num"][1].replace(",","").strip())
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num),comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num),click_num=VALUES(click_num)
        """

        params = (self["zhihu_id"], self["topics"], self["url"], self["title"], self["content"], self["answer_num"], self["comments_num"], watch_user_num, click_num, crawl_time)
        return insert_sql, params

class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num, create_time, update_time, crawl_time) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num),praise_num=VALUES(praise_num), update_tim=VALUES(update_time)
        """
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (self["zhihu_id"], self["url"], self["question_id"], self["author_id"], self["content"], self["praise_num"], self["comments_num"], create_time, update_time, self["crawl_time"].strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params

