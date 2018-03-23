from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from billiard import Process
from . import settings as config


class CrawlerScript():

    def __init__(self, options):
        self.options = options
        settings = Settings()
        settings.setmodule(config)

        if self.options.get('img_reduce_to'):
            images_thumbs = settings.get('IMAGES_THUMBS')
            images_thumbs['kindle'] = self.options.get('img_reduce_to')
            settings.set('IMAGES_THUMBS', images_thumbs)

        self.crawler = CrawlerProcess(settings)

    def _crawl(self, *args, **kwargs):
        self.crawler.crawl('mobi', *args, **kwargs)
        self.crawler.start()
        self.crawler.stop()

    def crawl(self, *args, **kwargs):
        if not kwargs.get('options'):
            kwargs.setdefault('options', self.options)
        p = Process(target=self._crawl, args=args, kwargs=kwargs)
        p.start()
        p.join()
