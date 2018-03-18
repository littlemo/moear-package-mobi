# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MoearPackageMobiItem(scrapy.Item):
    title = scrapy.Field()  # 文章标题
    cover_image = scrapy.Field()  # 文章封面图片
    content = scrapy.Field()  # 文章正文

    # 以下参数为pipelines处理时使用
    url_local = scrapy.Field()  # 文章持久化后的本地路径
    cover_image_local = scrapy.Field()  # 文章封面图片持久化后的本地路径

    image_urls = scrapy.Field()  # 图片链接
    images = scrapy.Field()  # 图片存储返回
