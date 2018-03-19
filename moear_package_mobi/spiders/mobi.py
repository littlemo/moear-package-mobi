# -*- coding: utf-8 -*-
import os
import re
import copy
import shutil
import tempfile

import scrapy
from jinja2 import Template
from scrapy.selector import Selector
from ..items import MoearPackageMobiItem

from moear_api_common import utils


class MobiSpider(scrapy.Spider):
    name = 'mobi'

    def __init__(self, data, spider, pkgmeta, usermeta, *args, **kwargs):
        self.data = data
        self.spider = spider
        self.pkgmeta = pkgmeta
        self.usermeta = usermeta

        # 关键字参数
        self._logger = kwargs.get('log', self.logger)
        self.debug = kwargs.get('debug', False)

        # 为了触发parse方法，就暂时辛苦下网络测试专用站啦（大雾~~
        self.start_urls = ['https://www.baidu.com']

        # 用于存储所有item的实例属性
        self.item_list = []

    def _initialize_debug_dir(self):
        if self.debug:
            self.output_directory = utils.mkdirp(os.path.join(
                self.base_dir, 'build', 'output'))
            temp = os.path.join(self.base_dir, 'build', 'temp')
            shutil.rmtree(temp, ignore_errors=True)
            self.tmpdir = utils.mkdirp(temp)

    def parse(self, response):
        """
        从self.data中将文章信息格式化为item
        """
        # 工作&输出路径
        self.base_dir = self.settings.get(
            'BASE_DIR',
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.template_dir = self.settings.get(
            'TEMPLATE_DIR',
            os.path.join(self.base_dir, 'template'))
        self.output_directory = tempfile.mkdtemp()
        self.tmpdir = tempfile.mkdtemp()

        # 获取Post模板对象
        template_post_path = os.path.join(self.template_dir, 'post.html')
        with open(template_post_path, 'r') as f:
            self.template_post = Template(f.read())

        self._initialize_debug_dir()

        self._logger.info('临时路径 => {0}'.format(self.tmpdir))
        self._logger.info('输出路径 => {0}'.format(self.output_directory))

        smeta = self.spider.get('meta', {})
        image_filter = smeta.get('image_filter', '')
        for sections in self.data.values():
            for p in sections:
                item = MoearPackageMobiItem()
                pmeta = p.get('meta', {})
                item['url'] = p.get('origin_url', '')
                item['title'] = p.get('title', '')
                item['cover_image'] = pmeta.get('moear.cover_image_slug')
                item['content'] = p.get('content', '')

                # 为图片持久化pipeline执行做数据准备
                item['image_urls'] = [item['cover_image']] \
                    if item['cover_image'] is not None else []
                item['image_urls'] += \
                    self._populated_image_urls_with_content(item['content'])
                self._logger.debug(
                    '待处理的图片url(过滤前): {}'.format(item['image_urls']))
                item['image_urls'] = self.filter_images_urls(
                    item['image_urls'], image_filter)
                self._logger.debug(
                    '待处理的图片url: {}'.format(item['image_urls']))

                yield item

    def _populated_image_urls_with_content(self, content):
        return Selector(
            text=content).css('img::attr(src)').extract()

    @staticmethod
    def filter_images_urls(image_urls, image_filter):
        rc = copy.deepcopy(image_urls)
        for i in image_urls:
            if isinstance(image_filter, str):
                if not image_filter:
                    break
                if re.search(image_filter, i):
                    rc.remove(i)
            elif isinstance(image_filter, list):
                if not all(image_filter):
                    break
                for f in image_filter:
                    if re.search(f, i):
                        rc.remove(i)
            else:
                raise TypeError('image_filter not str or list')
        return rc
