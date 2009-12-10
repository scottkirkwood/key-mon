#!/usr/bin/env python

from distutils.core import setup

NAME='key-mon'
VER='0.2'
setup(
    name = NAME,
    version = VER,
    packages = ['keymon'],
    package_dir = {
      'keymon': 'src/keymon'},
    package_data = {
      'keymon': ['themes/apple/*', 'themes/classic/*', '*.kbd'],
    },
    scripts=['src/key-mon'],
    author='Scott Kirkwood',
    author_email='scott@forusers.com',
    platforms=['POSIX'],
    license='GPL',
    keywords='keyboard status monitor',
    url=['http://code.google.com/p/%s' % NAME],
    download_url='http://%s.googlecode.com/files/%ss-%s.zip' % (NAME, NAME, VER),
    classifiers=[
    ], 
    
)
