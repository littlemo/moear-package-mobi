import os
import logging
import tempfile

from moear_api_common import base

from .crawler_script import CrawlerScript

log = logging.getLogger(__name__)


class Mobi(base.PackageBase):
    """
    Mobi打包

    用以实现基于kindlegen的mobi打包工具

    .. note::

        其中的模板实现，参考于
        `Kindle 期刊杂志格式排版的电子书制作教程 <https://www.imahui.com/notes/496.html>`_
    """
    def hook_custom_options(self):
        """
        该方法返回当前类的自定义配置项，由基类在 ``__init__`` 方法中调用，
        调用点位于，Common默认全局配置完成后，Spider元数据、用户元数据配置前

        :return: 返回当前类的自定义配置项
        :rtype: dict
        """
        return {
            'filename_extension': 'mobi',
            'kindlegen_unsupport_tag': [
                'iframe', 'audio', 'base',
                'canvas', 'command', 'datalist',
                'eventsource', 'form', 'input',
                'keygen', 'marquee', 'noscript',
                'param', 'video',
            ],
        }

    def generate(self, data, *args, **kwargs):
        """
        根据传入的数据结构生成最终用于推送的文件字节字符串( :func:`bytes` )，
        MoEar会将其持久化并用于之后的推送任务

        :param dict data: 待打包的数据结构
        :return: 返回生成的书籍打包输出字节
        :rtype: bytes
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.options.setdefault('package_build_dir', tmpdirname)
            crawler = CrawlerScript(self.options)
            crawler.crawl(data, self.spider, *args, **kwargs)

            output_file = os.path.join(
                self.options['package_build_dir'], 'source', 'moear.mobi')
            with open(output_file, 'rb') as fh:
                content = fh.read()

        return content
