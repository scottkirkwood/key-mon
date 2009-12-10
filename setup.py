#!/usr/bin/env python

from distutils.core import setup

NAME='key-mon'
VER='0.13'
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
    author_email='scott+keymon@forusers.com',
    platforms=['POSIX'],
    license='LGPL',
    keywords='keyboard status monitor education',
    url=['http://code.google.com/p/%s' % NAME],
    download_url='http://%s.googlecode.com/files/%ss-%s.zip' % (NAME, NAME, VER),
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: X11 Applications',
      'Intended Audience :: Education',
      'License :: OSI Approved :: GNU Library or Lesser General Public LIcense (LGPL)',
      'Operating System :: POSIX :: Linux',
      'Topic :: Education :: Computer Aided Instruction (CAI)',
    ], 
    description='',
    long_description=""" """,
)
