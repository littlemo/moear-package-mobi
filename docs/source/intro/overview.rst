.. _intro-overview:

====
概览
====

该项目实现了基于 `Scrapy`_ & `KindleGen`_ 的 ``mobi`` 打包功能，用于将文章列表打包，
供 `MoEar`_ 推送使用。

对于 `MoEar`_ 来说，并不强求打包插件使用何种技术实现，只要符合 `moear-api-common`_
中定义的相关接口即可。

当前主流的另一种实现为以 `KindleEar`_ 为主的，基于 `Calibre`_ 移植的打包工具包。
本工具实现时也有考虑使用 `Calibre`_ ，但由于其不支持 ``Python 3.X`` ，
且其实现为直接生成 ``mobi`` 文件，故涉及到很多的文件字节操作，在没有任何相关文档可参考的情况下，
实在是晦涩难懂，将其移植到 ``Python 3.X`` 下运行难度太高，故转而使用官方提供的转换工具。
庆幸的是，官方转换工具的使用，使得整个实现优雅简洁的多。


安装方法
========

您可以通过 ``pip`` 进行安装，本包仅在 ``Python 3.X`` 下测试通过::

    pip install moear-package-mobi


项目结构
========

包路径说明如下::

    .
    ├── __init__.py
    ├── crawler_script.py       # 用于提供可程序调用Scrapy的爬行类
    ├── entry.py                # 实现接口定义的入口文件
    ├── items.py                # Scrapy 的数据模型
    ├── middlewares.py          # Scrapy 的中间件
    ├── pipelines.py            # Scrapy 的流水线
    ├── settings.py             # Scrapy 的参数设置
    ├── spiders                 # Scrapy 的具体爬虫实现路径
    │   ├── __init__.py
    │   └── mobi.py             # mobi打包的爬虫主体
    └── template                # 模板路径，用来存储用于生成mobi源文件的Jinja模板
        ├── OEBPS
        │   ├── content.opf     # 内容清单模板
        │   ├── toc.html        # html格式的目录模板
        │   └── toc.ncx         # ncx格式的目录模板
        └── post.html           # 文章内容模板

.. attention::

    开发时注意需要在 ``setup.py`` 中添加如下配置，以便 `stevedore`_ 加载该插件::

        entry_points={
            'moear.package': [
                'mobi = moear_package_mobi.entry:Mobi',
            ],
        },

    参考 `stevedore`_ 文档，将第三行内容替换为您的具体实现即可


.. _MoEar: https://github.com/littlemo/moear
.. _Scrapy: https://github.com/scrapy/scrapy
.. _KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211
.. _moear-api-common: https://github.com/littlemo/moear-api-common
.. _KindleEar: https://github.com/cdhigh/KindleEar
.. _Calibre: https://github.com/kovidgoyal/calibre
.. _stevedore: https://docs.openstack.org/stevedore/latest/
