from setuptools import setup, find_packages

root_pack = 'moear_package_mobi.entry'


setup(
    name='moear-package-mobi',
    url='https://github.com/littlemo/moear-package-mobi',
    author='moear developers',
    author_email='moore@moorehy.com',
    maintainer='littlemo',
    maintainer_email='moore@moorehy.com',
    version='1.1.2',
    description='MoEar打包功能扩展插件 - Mobi',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='moear package scrapy',
    packages=find_packages(exclude=('docs', 'tests*')),
    include_package_data=True,
    zip_safe=False,
    license='GPLv3',
    python_requires='>=3',
    project_urls={
        'Documentation': 'http://moear-package-mobi.rtfd.io/',
        'Source': 'https://github.com/littlemo/moear-package-mobi',
        'Tracker':
            'https://github.com/littlemo/moear-package-mobi/issues',
    },
    install_requires=[
        'beautifulsoup4~=4.6.0',
        'billiard~=3.5.0.3',
        'Jinja2~=2.10',
        'moear-api-common~=1.0.2',
        'Pillow~=5.0.0',
        'Scrapy~=1.5.0',
    ],
    entry_points={
        'moear.package': [
            'mobi = {}:Mobi'.format(root_pack),
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Framework :: Scrapy',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Email',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Internet',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
)
