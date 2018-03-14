# -*- coding: utf-8 -*-
import os
import re
import json
import shutil
from collections import Iterable

import scrapy
from scrapy.selector import Selector
from spider.items import MoearPackageMobiItem

from moear_api_common import utils

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(base_dir, 'template')


class MobiSpider(scrapy.Spider):
    name = 'mobi'

    def __init__(self, data, spider, pkgmeta, usermeta, *args, **kwargs):
        self.data = data
        self.spider = spider
        self.pkgmeta = pkgmeta
        self.usermeta = usermeta

        # 关键字参数
        self._log = kwargs.get('log', self.logger)
        self.debug = kwargs.get('debug', False)

        # 工作&输出路径
        self.output_directory = tempfile.mkdtemp()
        self.tmpdir = tempfile.mkdtemp()
        if self.debug:
            self.output_directory = utils.mkdirp(os.path.join(
                base_dir, 'build', 'output'))
            self.tmpdir = utils.mkdirp(os.path.join(
                base_dir, 'build', 'temp'))

        self._initialize_tempdir()

    def _initialize_tempdir(self):
        self._log.info('临时路径 => {0}'.format(self.tmpdir))
        self._log.info('输出路径 => {0}'.format(self.output_directory))

        # 清除目标路径（主要用于处理调试时的指定路径）
        os.rmdir(self.tmpdir)

        shutil.copytree(template_dir, self.tmpdir)

    def parse(self, response):
        """
        从self.data中将文章信息格式化为item
        """
        for sections in self.data.values():
            for p in sections:
                item = MoearPackageMobiItem()
                pmeta = p.get('meta', {})
                image_filter = json.loads(
                    pmeta.get('moear.image_filter', ''),
                    encoding='UTF-8')
                item['cover_image'] = pmeta.get('moear.cover_image_slug')
                item['content'] = p.get('content', '')

                # 为图片持久化pipeline执行做数据准备
                item['image_urls'] = [item['cover_image']] \
                    if item['cover_image'] is not None else []
                item['image_urls'] += \
                    self._populated_image_urls_with_content(item['content'])
                self.logger.debug(
                    '待处理的图片url(过滤前): {}'.format(item['image_urls']))
                item['image_urls'] = self._filter_images_urls(
                    item['image_urls'], image_filter)
                self._log.debug('待处理的图片url: {}'.format(item['image_urls']))

    def _populated_image_urls_with_content(self, content):
        return Selector(
            text=content).css('img::attr(src)').extract()

    @staticmethod
    def filter_images_urls(image_urls, image_filter):
        assert isinstance(image_filter, Iterable)
        rc = []
        for i in image_urls:
            for f in image_filter:
                if not re.search(f, i):
                    rc.append(i)
        return rc
