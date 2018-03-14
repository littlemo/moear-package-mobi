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

        self._initialize_tempdir()

    def _initialize_tempdir(self):
        self._log.info('临时路径 => {0}'.format(self.tmpdir))
        self._log.info('输出路径 => {0}'.format(self.output_directory))

        # 清除目标路径（主要用于处理调试时的指定路径）
        os.rmdir(self.tmpdir)

        shutil.copytree(template_dir, self.tmpdir)

    def parse(self, response):
        pass
