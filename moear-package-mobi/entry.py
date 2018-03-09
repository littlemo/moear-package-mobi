import logging
import datetime

from moear_api_common import base
from moear_api_common.utils import makeoeb


log = logging.getLogger(__name__)


class Mobi(base.PackageBase):
    """
    Mobi打包
    ========

    用以实现mobi打包工具
    """
    def generate(self, data, spider, usermeta, *args, **kwargs):
        """
        生成
        ----

        根据传入的数据结构生成最终用于推送的文件字节字符串对象(byteStringIO)，
        MoEar会将其持久化并用于之后的推送任务

        额外接受的关键字参数：

        book_title: str, 书籍名称

        :params data dict: 待打包的数据结构
        :params spider dict: 指定爬虫的信息数据(包括 'meta' 字段的元数据字典，
            其中需包含书籍名称用的时间戳)
        :params usermeta dict: 指定用户的package相关配置元数据
        :returns: byteStringIO, 返回生成的书籍打包输出对象
        """
        opts = None
        oeb = None

        kw_book_title = kwargs.get('book_title')
        _log = kwargs.get('log', log)

        spidermeta = spider.get('meta', {})
        display_name = spider.get('display_name', '')

        device = usermeta.get('moear.package.device', 'kindle').lower()
        book_mode = spidermeta.get('book_mode', 'periodical')
        timestamp = spidermeta.get('timestamp', datetime.datetime.now())
        opts = makeoeb.getOpts(device, book_mode)
        oeb = makeoeb.CreateOeb(_log, None, opts)

        book_title = '_'.join([
            display_name if not kw_book_title else kw_book_title,
            timestamp.strftime('%Y%m%d%H%M%S')])

        pubtype = 'periodical:magazine:KindleEar' if book_mode != 'comic' \
            else 'book:book:KindleEar'

        language = spidermeta.get('language', 'zh-cn')

        makeoeb.setMetaData(
            oeb, book_title, language,
            timestamp.strftime('%Y%m%d%H%M%S'), pubtype=pubtype)
        oeb.container = makeoeb.ServerContainer(_log)
