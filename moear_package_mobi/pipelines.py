# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import codecs
import hashlib

from bs4 import BeautifulSoup

from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes


class MoEarImagesPipeline(ImagesPipeline):
    """
    定制ImagesPipeline，实现图片保存路径的自定义
    """
    def file_path(self, request, response=None, info=None):
        url = super(MoEarImagesPipeline, self).file_path(
            request, response=response, info=info)
        url = os.path.join('images', url)
        info.spider._logger.debug(
            '保存图片：{} | {} | {}'.format(response, request, url))
        return url


class PagePersistentPipeline(object):
    """
    将爬取到的文章内容持久化到指定路径
    """
    def process_item(self, item, spider):
        soup = BeautifulSoup(item.get('content', ''), "lxml")
        if item.get('images'):
            # 将content中的全部img替换为本地化后的url
            img_list = soup.find_all('img')
            for i in img_list:
                img_src = i.get('src')
                for result in item.get('images', []):
                    if img_src == result['url']:
                        # raw_path_list = result['path'].split('/')
                        i['src'] = os.path.join('..', result['path'])
                        spider._logger.debug(
                            '文章({})的正文img保存成功: {}'.format(
                                item['title'], img_src))
                        break

            # 填充toc_thumbnail路径值
            for result in item['images']:
                if item['cover_image'] == result['url']:
                    item['toc_thumbnail'] = result['path']
                    break
        item['content'] = str(soup.div)

        # 将item['content']保存到本地
        article_html_name = hashlib.sha1(to_bytes(item['url'])).hexdigest()
        html_name = '{}.html'.format(article_html_name)
        item['url_local'] = os.path.join('html', html_name)
        page_store = os.path.join(spider.tmpdir, item['url_local'])

        # 将item中的生成字段添加到post中
        idx = 0
        post = None
        for section in spider.data.items():
            for p in section[1]:
                idx += 1
                if p.get('origin_url') == item.get('url'):
                    post = p
                    p['idx'] = 'post_{:0>3}'.format(idx)
                    p['playOrder'] = idx
                    p['content'] = item.get('content')
                    p['url_local'] = item.get('url_local')
                    p['toc_thumbnail'] = item.get('toc_thumbnail')
                    break

        # 创建目标dirname
        dirname = os.path.dirname(page_store)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # 基于预设模板，将文章正文本地化
        with codecs.open(page_store, 'wb', 'utf-8') as fh:
            fh.write(spider.template_post.render(post=post))

        # 为优化log打印信息，清空已处理过的字段
        item.pop('content', '')
        item.pop('image_urls', [])
        item.pop('images', [])

        return item
