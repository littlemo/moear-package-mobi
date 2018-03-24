import os

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from billiard import Process
from . import settings as config


class CrawlerScript():

    def __init__(self, options):
        self.options = options
        settings = Settings()
        settings.setmodule(config)

        _build_dir = self.options.get('package_build_dir')
        _build_source_dir = os.path.join(_build_dir, 'source')
        _images_store = os.path.join(_build_source_dir, 'images')
        settings.set('BUILD_DIR', _build_dir)
        settings.set('BUILD_SOURCE_DIR', _build_source_dir)
        settings.set('IMAGES_STORE', _images_store)

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
