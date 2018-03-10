import sys
import logging
import unittest
from collections import OrderedDict

from moear_package_mobi import entry


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(message)s")  # output format
sh = logging.StreamHandler(stream=sys.stdout)  # output to standard output
sh.setFormatter(format)
log.addHandler(sh)


class TestSpiderEntryMethods(unittest.TestCase):
    """
    测试Mobi打包入口类的接口方法
    """
    def test_000_generate(self):
        """测试生成方法"""
        data = OrderedDict([
            ('热文', [
                ('为什么游戏玩不过我们会一直玩，学习学不明白就不学了？', '', 'https://pic2.zhimg.com/v2-11ee3463d0d3461f046ff95b5c339fa9.jpg', 'fake data'),
                ('圆周率里会出现你的银行卡密码吗？', '', 'https://pic3.zhimg.com/v2-1822222b9cac964fccf2d19876933d6e.jpg', 'fake data'),
                ('本周热门精选 · 人生荒废指北', '', 'https://pic3.zhimg.com/v2-6f6132eea92e4b10729bd1326ce260e2.jpg', 'fake data'),
                ('有哪些曾经很火，现在却被发现是很危险的发明？', '', 'https://pic3.zhimg.com/v2-532f361cb6cd77dd232696c0177d412a.jpg', 'fake data')
            ]),
            ('文章', [
                ('大误 · 《舌尖上的中国之：吸血鬼》', '', 'https://pic4.zhimg.com/v2-0c332103f9b14622a3c3ef5f495901df.jpg', 'fake data'),
                ('对方充错话费给我，却要我还？', '', 'https://pic3.zhimg.com/v2-54d36dbd969829e0c606827b921fb582.jpg', 'fake data'),
                ('瞎扯 · 如何正确地吐槽', '', 'https://pic1.zhimg.com/v2-8c6c38c1cc3c995d16c864e700d4745c.jpg', 'fake data')
            ])
        ])
        spider = {
            'name': 'zhihudaily',
            'display_name': '知乎日报',
            'author': '小貘',
            'email': 'xxx@xxx.com',
            'description': '何时找到女盆友',
            'meta': {
                'language': 'zh-cn',
                'book_mode': 'periodical',
            }
        }
        usermeta = {
            'moear.package.device': 'kindle'
        }
        rc = entry.Mobi().generate(data, spider, usermeta)
        log.info(rc)
        self.assertIsInstance(rc, str)
