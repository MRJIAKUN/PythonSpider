# -*- coding: utf-8 -*-
'''
使用scrapy模拟登陆知乎
'''

import scrapy
import re
import json
import datetime

from urllib import parse
from MySpider.items import ArticleItemLoader, ZhihuAnswerItem, ZhihuQuestionItem



class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    # question的第一页answer的请求Url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics&limit={1}&offset={2}"

    agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": agent
    }

    def parse(self, response):
        '''
        提取出html页面中的所有url 并跟踪url进行进一步爬取
        如果提取的url格式为/question/xxx就下载之后直接进入解析函数
        :param response:
        :return:
        '''

        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = int(match_obj.group(2))

                yield scrapy.Request(request_url, headers=self.headers, meta={"question_id":question_id},callback=self.parse_question)
            else:
                yield scrapy.Request(url, headers=self.headers, callback=parse)


    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def login(self, response):
        response_text  = response.text
        # 用正则表达式取出xsrf,  re.DOTALL对所有数据进行匹配
        match_obj = re.match('.* name="_xsrf" value="(.*?)"', response.text.encode("utf-8"), re.DOTALL)
        xsrf = ""
        if match_obj:
            xsrf = (match_obj.group(1))

        if xsrf:
            return [scrapy.FormRequest(
                url="https://www.zhihu.com/login/phone_num",
                formdata = {
                    "_xsrf": xsrf,
                    "phone_num": "13144485182",
                    "password": "CAISIYUAN"
            },
                headers=self.headers,
                callback=self.check_login
            )]


    def check_login(self,response):
        # 验证是否登陆成功
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] =="登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)


    def parse_question(self, response):
        question_item_loader = ArticleItemLoader(item=ZhihuQuestionItem(), response=response)
        question_item_loader.add_css("title", "h1.QuestionHeader-title::text")
        question_item_loader.add_css("content", ".QuestionHeader-detail")
        question_item_loader.add_value("url", response.url)
        question_item_loader.add_value("zhihu_id", response.meta.get("question_id", ""))
        question_item_loader.add_css("answer_num", ".List-headerText span::text")
        question_item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
        question_item_loader.add_css("watch_user_num",".NumberBoard-itemValue::text")
        question_item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
        question_item = question_item_loader.load_item()

        yield scrapy.Request(self.start_answer_url, format(response.meta.get("question_id", ""), 20, 0), headers=self.headers, callback=self.parse_answer)

        yield question_item


    def parse_answer(self,response):
        answer_json = json.loads(response.text)
        is_end = answer_json["paging"]["in_end"]
        totals = answer_json["paging"]["totals"]
        next_url = answer_json["paging"]["next"]

        # 提取answer具体数据
        for answer in answer_json["data"]:
            answer_itme = ZhihuAnswerItem()
            answer_itme["zhihu_id"] = answer["id"]
            answer_itme["url"] = answer["url"]
            answer_itme["question_id"] = answer["question"]["id"]
            answer_itme["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_itme["content"] = answer["contnet"] if "content" in answer else None
            answer_itme["parise_num"] = answer["voteup_count"]
            answer_itme["comments_num"] = answer["comment_count"]
            answer_itme["create_time"] = answer["created_time"]
            answer_itme["update_time"] = answer["updated_time"]
            answer_itme["crawl_tiem"] = datetime.datetime.now()

            yield answer_itme

        if not is_end:
            yield scrapy.Request(next_url, format(response.meta.get("question_id", ""), 20, 0),
                                 headers=self.headers, callback=self.parse_answer)