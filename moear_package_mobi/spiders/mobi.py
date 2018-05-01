# -*- coding: utf-8 -*-
import os
import re
import copy
import json
import codecs
import shutil
import datetime
import subprocess

import scrapy
from jinja2 import Environment
from jinja2 import Template
from scrapy.selector import Selector
from ..items import MoearPackageMobiItem

from moear_api_common import utils
from moear_api_common.utils import kindlegen


class MobiSpider(scrapy.Spider):
    '''
    打包爬虫，主要工作为将文章内容中的图片进行本地化、压缩、灰度，最终基于
    `KindleGen <https://www.amazon.com/gp/feature.html?docId=1000765211>`_
    工具，打包输出为 ``mobi`` 格式的电子书
    '''
    name = 'mobi'

    def __init__(self, data, spider, *args, **kwargs):
        self.data = data
        self.spider = spider
        self.options = kwargs.get('options')

        if not self.options:
            raise ValueError('未传入 options 关键字参数')

        # 关键字参数
        self._logger = kwargs.get('log', self.logger)

        # 设置 publish_date 默认值
        if not self.options.get('publish_date'):
            self.options['publish_date'] = datetime.date.today() \
                .strftime('%Y-%m-%d')

        # 获取 data 中的总文章数
        self.post_num = 0
        for section in data.items():
            self.post_num += len(section[1])
        self._logger.info('文章总数: {}'.format(self.post_num))

        # 获取并设置 kindlegen 文件路径
        kindlegen_path = self.options.get('kindlegen_path', '')
        self.kg = kindlegen.find_kindlegen_prog(kindlegen_path)
        self._logger.debug('检测到 KindleGen => {}'.format(self.kg))
        if not self.kg:
            raise ValueError('未检测到 KindleGen 文件路径')

        # 为了触发parse方法，就暂时辛苦下网络测试专用站啦（大雾~~
        self.start_urls = ['https://www.baidu.com']

        self.jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])

    def parse(self, response):
        """
        从 self.data 中将文章信息格式化为 :class:`.MoearPackageMobiItem`
        """
        # 工作&输出路径
        self.template_dir = self.settings.get('TEMPLATE_DIR')
        shutil.rmtree(
            self.settings.get('BUILD_SOURCE_DIR'), ignore_errors=True)
        self.build_source_dir = utils.mkdirp(
            self.settings.get('BUILD_SOURCE_DIR'))

        # 获取Post模板对象
        template_post_path = os.path.join(self.template_dir, 'post.html')
        with open(template_post_path, 'r') as f:
            self.template_post = Template(f.read())

        self._logger.info('构建处理路径 => {0}'.format(self.build_source_dir))

        image_filter = self.options.get('image_filter', '')
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
                item['image_urls'], item['image_urls_removed'] = \
                    self.filter_images_urls(
                        item['image_urls'], image_filter)
                self._logger.debug(
                    '待处理的图片url: {}'.format(item['image_urls']))

                yield item

    def _populated_image_urls_with_content(self, content):
        return Selector(
            text=content).css('img::attr(src)').extract()

    @staticmethod
    def filter_images_urls(image_urls, image_filter):
        '''
        图片链接过滤器，根据传入的过滤器规则，对图片链接列表进行过滤并返回结果列表

        :param list(str) image_urls: 图片链接字串列表
        :param list(str) image_filter: 过滤器字串列表
        :return: 过滤后的结果链接列表，以及被过滤掉的链接列表
        :rtype: list(str), list(str)
        '''
        image_filter = json.loads(image_filter, encoding='utf-8')
        rc = copy.deepcopy(image_urls)
        rc_removed = []
        for i in image_urls:
            if isinstance(image_filter, str):
                if not image_filter:
                    break
                if re.search(image_filter, i):
                    rc.remove(i)
                    rc_removed.append(i)
            elif isinstance(image_filter, list):
                if not all(image_filter):
                    break
                for f in image_filter:
                    if re.search(f, i):
                        rc.remove(i)
                        rc_removed.append(i)
            else:
                raise TypeError('image_filter not str or list')
        return rc, rc_removed

    def generate_mobi_file(self):
        '''
        使用 :mod:`subprocess` 模块调用 ``KindleGen`` 工具，
        将已准备好的书籍源文件编译生成 ``mobi`` 文件
        '''
        opf_file = os.path.join(self.build_source_dir, 'moear.opf')
        command_list = [self.kg, opf_file]
        output = subprocess.Popen(
            command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=False).communicate()
        self._logger.info('生成命令: {}'.format(' '.join(command_list)))
        self._logger.info('生成 mobi : {}'.format(
            output[0].decode()))
        if output[1]:
            self._logger.error(output[1].decode())
            raise IOError('KindleGen转换失败: {}'.format(output[1]))

    def closed(self, reason):
        '''
        异步爬取本地化处理完成后，使用结果数据，进行输出文件的渲染，渲染完毕，
        调用 :meth:`.MobiSpider.generate_mobi_file` 方法，生成目标 ``mobi`` 文件
        '''
        # 拷贝封面&报头图片文件
        utils.mkdirp(os.path.join(self.build_source_dir, 'images'))
        self._logger.info(self.options)
        shutil.copy(
            self.options.get('img_cover'),
            os.path.join(self.build_source_dir, 'images', 'cover.jpg'))
        shutil.copy(
            self.options.get('img_masthead'),
            os.path.join(self.build_source_dir, 'images', 'masthead.gif'))

        # 拷贝css文件
        css_base_path = self.options.get('css_base')
        css_package_path = self.options.get('css_package')
        css_extra = self.options.get('extra_css', '')
        css_output_dir = os.path.join(self.build_source_dir, 'css')
        utils.mkdirp(css_output_dir)
        if css_base_path:
            shutil.copy(
                css_base_path,
                os.path.join(css_output_dir, 'base.css'))
        if css_package_path:
            shutil.copy(
                css_package_path,
                os.path.join(css_output_dir, 'package.css'))
        if css_extra:
            with codecs.open(
                    os.path.join(css_output_dir, 'custom.css'),
                    'wb', 'utf-8') as fh:
                fh.write(css_extra)

        # 拷贝icons路径文件
        icons_path = self.options.get('icons_path')
        icons_output_dir = os.path.join(self.build_source_dir, 'icons')
        shutil.rmtree(icons_output_dir, ignore_errors=True)
        if icons_path:
            shutil.copytree(icons_path, icons_output_dir)

        # 获取content模板对象
        template_content_path = os.path.join(
            self.template_dir, 'OEBPS', 'content.opf')
        with open(template_content_path, 'r') as fh:
            template_content = Template(fh.read())

        # 渲染content目标文件
        content_path = os.path.join(self.build_source_dir, 'moear.opf')
        with codecs.open(content_path, 'wb', 'utf-8') as fh:
            fh.write(template_content.render(
                data=self.data,
                spider=self.spider,
                options=self.options))

        # 获取toc.ncx模板对象
        template_toc_path = os.path.join(
            self.template_dir, 'OEBPS', 'toc.ncx')
        with open(template_toc_path, 'r') as fh:
            template_toc = Template(fh.read())

        # 渲染toc.ncx目标文件
        toc_path = os.path.join(self.build_source_dir, 'misc', 'toc.ncx')
        utils.mkdirp(os.path.dirname(toc_path))
        with codecs.open(toc_path, 'wb', 'utf-8') as fh:
            fh.write(template_toc.render(
                data=self.data,
                spider=self.spider,
                options=self.options))

        # 获取toc.html模板对象
        template_toc_path = os.path.join(
            self.template_dir, 'OEBPS', 'toc.html')
        with open(template_toc_path, 'r') as fh:
            template_toc = Template(fh.read())

        # 渲染toc.html目标文件
        toc_path = os.path.join(self.build_source_dir, 'html', 'toc.html')
        utils.mkdirp(os.path.dirname(toc_path))
        with codecs.open(toc_path, 'wb', 'utf-8') as fh:
            fh.write(template_toc.render(
                data=self.data,
                options=self.options))

        # 生成mobi文件到mobi_dir
        self.generate_mobi_file()
