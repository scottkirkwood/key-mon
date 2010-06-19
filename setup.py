#!/usr/bin/env python

from distutils.core import setup
import re

# setup.py sdist --formats=gztar,zip upload
# setup.py bdist

NAME='key-mon'
DIR='src/keymon'
PY_NAME='key_mon'
DEB_NAME=NAME.replace('-', '')
VER='1.1'

PY_SRC='%s.py' % PY_NAME
DEPENDS=['python-xlib']
MENU_SUBSECTION='Graphics'
DEPENDS_STR=' '.join(DEPENDS)
AUTHOR_NAME='Scott Kirkwood'
KEYWORDS=['keyboard', 'status', 'monitor', 'education']

SETUP = dict(
  name = NAME,
  version = VER,
  packages = ['keymon'],
  package_dir = {
      'keymon': 'src/keymon'},
  package_data = {
      'keymon': ['themes/apple/*', 'themes/classic/*', '*.kbd'],
  },
  scripts=['src/key-mon'],
  author=AUTHOR_NAME,
  author_email='scott+keymon@forusers.com',
  platforms=['POSIX'],
  license='GPL',
  keywords=' '.join(KEYWORDS),
  url='http://code.google.com/p/%s' % NAME,
  download_url='http://%s.googlecode.com/files/%s-%s.zip' % (NAME, NAME, VER),
  description='A screencast utility that displays your keyboard and mouse status.',
  long_description="""Key-mon is useful for teaching since it shows the current status of your
  keyboard and mouse and you use them in another application.  No longer do you need to say
  'Now I'm pressing the Ctrl-D key', your students can just see the keystroke for themselves.
  """,
  classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: X11 Applications',
      'Intended Audience :: Education',
      'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
      'Operating System :: POSIX :: Linux',
      'Topic :: Education :: Computer Aided Instruction (CAI)',
  ],
)

COPYRIGHT = 'Copyright (C) 2010 %s' % (AUTHOR_NAME) # pylint: disable-msg=W0622
LICENSE_TITLE = 'GNU General Public License'
LICENSE_SHORT = 'GPL'
LICENSE_VERSION = '3'
LICENSE_TITLE_AND_VERSION = '%s version %s' % (LICENSE_TITLE, LICENSE_VERSION)
LICENSE = '%s or any later version' % LICENSE_TITLE_AND_VERSION # pylint: disable-msg=W0622
LICENSE_TITLE_AND_VERSION_ABBREV = 'GPLv%s' % LICENSE_VERSION
LICENSE_ABBREV = '%s+' % LICENSE_TITLE_AND_VERSION_ABBREV
LICENSE_NOTICE = '''%(name)s is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

%(name)s is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.''' % dict(name=NAME)

LICENSE_NOTICE_HTML = '<p>%s</p>' % LICENSE_NOTICE.replace('\n\n', '</p><p>')
LICENSE_NOTICE_HTML = re.sub(r'<http([^>]*)>', r'<a href="http\1" target="_blank">http\1</a>', LICENSE_NOTICE_HTML)

if __name__ == '__main__':
  setup(**SETUP)
