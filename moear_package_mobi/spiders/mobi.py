# -*- coding: utf-8 -*-
import os
import shutil

import scrapy

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

    def parse(self, response):
        pass
