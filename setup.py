#!/usr/bin/python
from setuptools import setup, find_packages

NAME='key-mon'
VER='0.2'
setup(
    name = NAME,
    version = VER,
    packages = find_packages('.'),
    package_dir = {'': '.', 'svg': 'svg'},
    install_requires = ['pygtk>=2.0'],
    include_package_data = True,
    package_data = {
        '': ['*.svg'],
    },
    author='Scott Kirkwood',
    author_email='scott@forusers.com',
    platforms=['POSIX'],
    license='GPL',
    keywords='keyboard status monitor',
    url=['http://code.google.com/p/%s' % NAME],
    download_url='http://%s.googlecode.com/files/%ss-%s.zip' % (NAME, NAME, VER),
    zip_safe=False,
    classifiers=[
    ], 
    
)
