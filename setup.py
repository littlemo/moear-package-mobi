from setuptools import setup, find_packages

root_pack = 'moear_package_mobi.entry'


setup(
    name='moear-package-mobi',
    url='https://github.com/littlemo/moear-package-mobi',
    author='moear developers',
    author_email='moore@moorehy.com',
    maintainer='littlemo',
    maintainer_email='moore@moorehy.com',
    version='1.0.0',
    description='MoEar扩展打包功能插件 - Mobi',
    long_description='test',
    keywords='moear package',
    packages=find_packages(exclude=('docs', 'tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    license='GPLv3',
    provides=[
        'moear.api',
    ],
    install_requires=[
        'moear-api-common~=1.0.0',
    ],
    entry_points={
        'moear.package': [
            'mobi = {}:Mobi'.format(root_pack),
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
)
