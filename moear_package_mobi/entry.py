import logging
import datetime

from moear_api_common import base


log = logging.getLogger(__name__)


class Mobi(base.PackageBase):
    """
    Mobi打包
    ========

    用以实现基于kindlegen的mobi打包工具
    """
    def __init__(self, spider, *args, **kwargs):
        super(Mobi, self).__init__(spider, *args, **kwargs)

        # 钩子配置，用以在全局变量初始化后进行当前打包类的定制配置
        # 注意此处应配置打包类相关的定制配置，具体爬虫相关的配置应设置在相应爬虫的元数据中
        self.configure({})

    def generate(self, data, *args, **kwargs):
        """
        生成
        ----

        根据传入的数据结构生成最终用于推送的文件字节字符串对象(byteStringIO)，
        MoEar会将其持久化并用于之后的推送任务

        额外接受的关键字参数：

        book_title: str, 书籍名称

        :params data dict: 待打包的数据结构
        :returns: str, 返回生成的书籍打包输出字符串
        """
        crawler = CrawlerScript()
        crawler.crawl(data, self.spider, self.options, *args, **kwargs)
        # 准备基础参数
        opts = None
        oeb = None

        kw_book_title = kwargs.get('book_title')
        _log = kwargs.get('log', log)

        spidermeta = spider.get('meta', {})
        display_name = spider.get('display_name', '')

        device = usermeta.get('moear.package.device', 'kindle').lower()

        language = spidermeta.get('language', 'zh-cn')
        book_mode = spidermeta.get('book_mode', 'periodical')
        timestamp = spidermeta.get('timestamp', datetime.datetime.now())
        img_cover = spidermeta.get(
            'img_cover', self.settings.get('img_cover'))
        img_masthead = spidermeta.get(
            'img_masthead', self.settings.get('img_masthead'))
        toc_desc_generate = spidermeta.get(
            'toc_desc_generate', self.settings.get('toc_desc_generate'))
        toc_thumbnail_generate = spidermeta.get(
            'toc_thumbnail_generate',
            self.settings.get('toc_thumbnail_generate'))

        # 创建并配置OEB对象
        opts = makeoeb.getOpts(device, book_mode)
        oeb = makeoeb.CreateOeb(_log, None, opts)

        book_title = '_'.join([
            display_name if not kw_book_title else kw_book_title,
            timestamp.strftime('%Y%m%d%H%M%S')])

        pubtype = 'periodical:magazine:KindleEar' if book_mode != 'comic' \
            else 'book:book:KindleEar'

        makeoeb.setMetaData(
            oeb, book_title, language,
            timestamp.strftime('%Y%m%d%H%M%S'), pubtype=pubtype)
        oeb.container = makeoeb.ServerContainer(_log)

        # guide, masthead
        id_, href = oeb.manifest.generate('masthead', img_masthead)
        oeb.manifest.add(id_, href, makeoeb.MimeFromFilename(img_masthead))
        oeb.guide.add('masthead', 'Masthead Image', href)

        # guide, cover
        id_, href = oeb.manifest.generate('cover', img_cover)
        oeb.manifest.add(id_, href, makeoeb.MimeFromFilename(img_cover))
        oeb.guide.add('cover', 'Cover', href)
        oeb.metadata.add('cover', id_)

        # 插入目录
        sections = data
        toc_thumbnails = {}
        insertHtmlToc = toc_desc_generate
        insertThumbnail = toc_thumbnail_generate
        self.insert_toc(
            oeb, sections, toc_thumbnails, insertHtmlToc, insertThumbnail)

        # 转换输出
        oIO = byteStringIO()
        o = MOBIOutput()
        o.convert(oeb, oIO, opts, _log)
        _log.info("%s.mobi Sent!" % (book_title))
        return str(oIO.getvalue())
