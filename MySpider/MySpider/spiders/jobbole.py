# -*- coding: utf-8 -*-
import scrapy
import re
import datetime


from scrapy.http import Request
from urllib import parse

from items import JobBoleArticleItem, ArticleItemLoader
from utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1. 获取文章列表页中的文章url并交给解析函数进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse函数
        :param response:
        :return:
        '''

        # 解析文章列表页中文章url
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        # 有些url可能不带域名，所以这里用parse的urljoin方法把域名join起来，用callback进行函数的回调
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail)
        # 获取下一页文章列表的url地址
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)



    def parse_detail(self,response):
        '''
        解析文章详情
        :param response:
        :return:
        '''

        # 实例化item
        article_item = JobBoleArticleItem()
        # 使用xpath来获取数据
        # #// *[ @ id = "post-114041"] / div[1] / h1
        # title = response.xpath("//*[@id='post-114041']/div/h1/text()").extract_first("")
        # create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract_first("").strip().replace("·","").strip()
        # praise_nums = response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract_first("")
        # fav_nums = response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract_first("")
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = match_re.group(1)
        # comment_nums = response.xpath("//a[href='#article-comment']/span/text()").extract_first("")
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = match_re.group(1)
        # content = response.xpath("//div[class='entry']").extract()extract_first("")
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract_first("")
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)

        # 使用css选择器来获取数据

        # extract_first函数:extract返回的是一个数组，数组有可能为空，所以取第0个值得时候会报错，调用这个函数可以在取不到值得时候给一个默认值
        # title = response.css(".entry-header h1::text").extract_first("")
        # create_date = response.css(".entry-meta-hide-on-mobile::text").extract_first("").strip().replace("·","").strip()
        # praise_nums = response.css(".vote-post-up h10::text").extract_first("")
        # fav_nums = response.css(".bookmark-btn::text").extract_first("")
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.css("a[href='#article-comment'] span::text").extract_first("")
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.css("div.entry").extract_first("")
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)

        front_image_url = response.meta.get("front_image_url", "")

        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["front_image_path"]
        #通过item loader加载item
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_date",".entry-meta-hide-on-mobile::text")
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])

        article_item = item_loader.load_item()
        yield article_item

