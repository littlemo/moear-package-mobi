# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
import codecs
import hashlib

from bs4 import BeautifulSoup

from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes

from moear_api_common.utils import img


class MoEarImagesPipeline(ImagesPipeline):
    """
    实现图片定制化处理操作
    """
    def file_path(self, request, response=None, info=None):
        url = super(MoEarImagesPipeline, self).file_path(
            request, response=response, info=info)
        info.spider._logger.debug(
            '保存图片：{} | {} | {}'.format(response, request, url))
        return url

    def item_completed(self, results, item, info):
        '''
        在正常图片本地化处理管道业务执行完毕后，使用缩略图路径替换原 ``result[path]`` 路径，
        从而使最终打包时使用缩略图，并根据配置，对缩略图进行灰度处理

        :param item: 爬取到的数据模型
        :type item: :class:`.MoearPackageMobiItem` or dict
        '''
        # 处理 results 中的 path 使用缩略图路径替代
        for ok, result in results:
            if not ok:
                continue
            path = result['path']
            path = re.sub(r'full', os.path.join('thumbs', 'kindle'), path)
            result['path'] = path

        # 处理缩略图为灰度图，为便于在电纸书上节省空间
        if info.spider.options.get('img_convert_to_gray'):
            images_store = info.spider.settings.get('IMAGES_STORE')
            for ok, result in results:
                if not ok:
                    continue

                img_path = os.path.join(images_store, result['path'])
                with open(img_path, 'rb+') as fh:
                    output = img.gray_image(fh.read())
                    fh.seek(0)
                    fh.truncate()
                    fh.write(output)

        info.spider._logger.debug(results)
        item = super(MoEarImagesPipeline, self).item_completed(
            results, item, info)
        return item


class PagePersistentPipeline(object):
    """
    将爬取到的文章内容本地化到指定路径
    """
    def process_item(self, item, spider):
        '''
        将从图片处理管道流过的数据模型中的缩略图链接更新到文章中的相应图片 URL 上，
        并对其中的，已删除图片 ``item['image_urls_removed']`` 进行处理，
        使其显示内建的删除图标。

        最终使用文章模板，对数据模型中的数据进行渲染并输出到指定路径中，完成本地化，
        等待最终 ``mobi`` 打包

        :param item: 爬取到的数据模型
        :type item: :class:`.MoearPackageMobiItem` or dict
        :param spider: 当前爬虫对象
        :type spider: :class:`.MobiSpider`
        '''
        soup = BeautifulSoup(item.get('content', ''), "lxml")
        if item.get('images'):
            # 将content中的全部img替换为本地化后的url
            img_list = soup.find_all('img')
            for i in img_list:
                img_src = i.get('src')

                # 删除image_urls_removed中的img，避免由于未本地化造成mobi生成失败
                if img_src in item.get('image_urls_removed', []):
                    i['src'] = '../icons/delete.jpg'

                for result in item.get('images', []):
                    if img_src == result['url']:
                        i['src'] = os.path.join('..', 'images', result['path'])
                        spider._logger.debug(
                            '文章({})的正文img保存成功: {}'.format(
                                item['title'], img_src))
                        break

            # 填充toc_thumbnail路径值
            for result in item['images']:
                if item['cover_image'] == result['url']:
                    item['toc_thumbnail'] = os.path.join(
                        'images', result['path'])
                    break

        # 过滤掉不支持的标签
        unsupport_tag = spider.options.get('kindlegen_unsupport_tag', [])
        for tag in unsupport_tag:
            for i in soup.find_all(tag):
                delete_img = soup.new_tag('img')
                delete_img['src'] = '../icons/delete.jpg'
                i.replace_with(delete_img)

        item['content'] = str(soup.div)

        # 将item['content']保存到本地
        article_html_name = hashlib.md5(to_bytes(item['url'])).hexdigest()
        html_name = '{}.html'.format(article_html_name)
        item['url_local'] = os.path.join('html', html_name)
        page_store = os.path.join(spider.build_source_dir, item['url_local'])

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

                    # 若为最后一篇文章，则添加相应标志
                    if idx == spider.post_num:
                        spider._logger.info(
                            '标记为最后一篇文章: {}'.format(p.get('title')))
                        p['last_one'] = True
                    break

        # 创建目标dirname
        dirname = os.path.dirname(page_store)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # 基于预设模板，将文章正文本地化
        with codecs.open(page_store, 'wb', 'utf-8') as fh:
            fh.write(spider.template_post.render(
                post=post,
                options=spider.options))

        # 为优化log打印信息，清空已处理过的字段
        item.pop('content', '')
        item.pop('image_urls', [])
        item.pop('images', [])

        return item
