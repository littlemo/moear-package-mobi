import sys
import json
from json.decoder import JSONDecodeError
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
    def setUp(self):
        self.image_urls = [
            'https://pic3.zhimg.com/v2-75f1aab89899b07ea0b2c642ea647662.jpg',
            'https://pic3.zhimg.com/v2-46e7a28b89f7e5351355af36c7221cee.jpg',
            'https://pic2.zhimg.com/equation?tex=f7e5351355af36c7221cee.jpg',
        ]
        self.image_filter = json.dumps(['com/v2-46e7a', 'equation\\?tex='])

    def test_000_filter_images_urls_with_list_filter(self):
        """测试传入列表过滤器到图片链接列表过滤器方法中"""
        rc, rc_removed = mobi.MobiSpider.filter_images_urls(
            self.image_urls, self.image_filter)
        log.debug(rc)
        self.assertNotIn(self.image_urls[1], rc)
        self.assertNotIn(self.image_urls[2], rc)
        self.assertIn(self.image_urls[1], rc_removed)
        self.assertIn(self.image_urls[2], rc_removed)

    def test_001_filter_images_urls_with_str_filter(self):
        """测试传入单字串过滤器参数到图片列表过滤器方法中"""
        rc, rc_removed = mobi.MobiSpider.filter_images_urls(
            self.image_urls, json.dumps(['equation\\?tex=']))
        log.debug(rc)
        self.assertNotIn(self.image_urls[2], rc)
        self.assertIn(self.image_urls[2], rc_removed)

    def test_002_filter_images_urls_with_invalid_filter(self):
        """测试传入非法类型的过滤器参数到图片列表过滤器中"""
        try:
            mobi.MobiSpider.filter_images_urls(
                self.image_urls, 'equation\\\\?tex=')
            raise Exception('未如预期抛出 JSONDecodeError')
        except Exception as e:
            self.assertTrue(isinstance(e, JSONDecodeError))

    def test_003_filter_images_urls_with_null_str_filter(self):
        """测试传入空字符串类型的过滤器参数到图片列表过滤器中"""
        rc, rc_removed = mobi.MobiSpider.filter_images_urls(
            self.image_urls, json.dumps([""]))
        log.debug(rc)
        self.assertEqual(rc, self.image_urls)
        self.assertEqual(rc_removed, [])

    def test_004_filter_images_urls_with_null_list_filter(self):
        """测试传入空字符串类型的过滤器参数到图片列表过滤器中"""
        rc, rc_removed = mobi.MobiSpider.filter_images_urls(
            self.image_urls, json.dumps([]))
        log.debug(rc)
        self.assertEqual(rc, self.image_urls)
        self.assertEqual(rc_removed, [])
