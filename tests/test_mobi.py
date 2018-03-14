import sys
import logging
import unittest

from moear_package_mobi.spiders import mobi


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
format = logging.Formatter("%(asctime)s - %(message)s")  # output format
sh = logging.StreamHandler(stream=sys.stdout)  # output to standard output
sh.setFormatter(format)
log.addHandler(sh)


class TestSpiderMobiMethods(unittest.TestCase):
    """
    测试Mobi打包类
    """
    def test_000_filter_images_urls(self):
        """测试图片链接列表过滤器正常功能"""
        image_urls = [
            'https://pic3.zhimg.com/v2-75f1aab89899b07ea0b2c642ea647662.jpg',
            'https://pic3.zhimg.com/v2-46e7a28b89f7e5351355af36c7221cee.jpg',
            'https://pic2.zhimg.com/equation?tex=f7e5351355af36c7221cee.jpg',
        ]
        image_filter = (
            'equation\?tex=',
        )
        rc = mobi.MobiSpider.filter_images_urls(image_urls, image_filter)
        log.debug(rc)
        self.assertNotIn(
            'https://pic3.zhimg.com/equation?tex=f7e5351355af36c7221cee.jpg',
            rc)
