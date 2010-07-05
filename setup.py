#!/usr/bin/env python
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from distutils.core import setup
import re

NAME = 'key-mon'
VER = '1.2.3'
DIR = 'src/keymon'
PY_NAME = 'key_mon'
DEB_NAME = NAME.replace('-', '')
RELEASE_FILE = 'docs/RELEASE.rst'

PY_SRC = '%s.py' % PY_NAME
DEPENDS = ['python-xlib', 'python-gtk2']
DEPENDS_STR = ' '.join(DEPENDS)

MENU_SUBSECTION = 'Graphics'
AUTHOR_NAME = 'Scott Kirkwood'
COPYRIGHT_NAME = 'Google Inc.'
GOOGLE_CODE_EMAIL = 'scott@forusers.com'
KEYWORDS = ['keyboard', 'status', 'monitor', 'education']
MAN_FILE = 'man/%s.1' % NAME
DESKTOP_FILE = 'icons/%s.desktop' % NAME
ICON = 'icons/key-mon.xpm'
COMMAND = '/usr/bin/%s' % NAME

SETUP = dict(
  name=NAME,
  version=VER,
  packages=['keymon'],
  package_dir={
      'keymon': 'src/keymon'},
  package_data = {
      'keymon': ['themes/apple/*', 'themes/classic/*', '*.kbd', 'icons/key-mon.desktop'],
  },
  scripts=['src/key-mon'],
  author=AUTHOR_NAME,
  author_email='scott+keymon@forusers.com',
  platforms=['POSIX'],
  license='Apache 2.0',
  keywords=' '.join(KEYWORDS),
  url='http://code.google.com/p/%s' % NAME,
  download_url='http://%s.googlecode.com/files/%s-%s.zip' % (NAME, NAME, VER),
  description='A screencast utility that displays your keyboard and mouse status',
  long_description="""Key-mon is useful for teaching since it shows the current status of your
  keyboard and mouse and you use them in another application.  No longer do you need to say
  'Now I'm pressing the Ctrl-D key', your students can just see the keystroke for themselves.
  """,
  classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: X11 Applications',
      'Intended Audience :: Education',
      'License :: OSI Approved :: Apache Software License',
      'Operating System :: POSIX :: Linux',
      'Topic :: Education :: Computer Aided Instruction (CAI)',
  ],
  #zip_safe=False,
)

COPYRIGHT = 'Copyright (C) 2010 %s' % (COPYRIGHT_NAME) # pylint: disable-msg=W0622
LICENSE_TITLE = 'Apache License'
LICENSE_SHORT = 'Apache'
LICENSE_VERSION = '2.0'
LICENSE_TITLE_AND_VERSION = '%s version %s' % (LICENSE_TITLE, LICENSE_VERSION)
LICENSE = '%s or any later version' % LICENSE_TITLE_AND_VERSION # pylint: disable-msg=W0622
LICENSE_TITLE_AND_VERSION_ABBREV = '%s v%s' % (LICENSE_SHORT, LICENSE_VERSION)
LICENSE_ABBREV = '%s+' % LICENSE_TITLE_AND_VERSION_ABBREV
LICENSE_URL = 'http://www.apache.org/licenses/LICENSE-2.0'
LICENSE_PATH = '/usr/share/common-licenses/Apache-2.0'
LICENSE_NOTICE = '''%(name)s is free software: you can redistribute it and/or modify
it under the terms of the Apache License as published by
the Apache Software Foundation, either version 2 of the License, or
(at your option) any later version.

%(name)s is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the Apache License
along with this program.  If not, see <%(url)s>.''' % dict(name=NAME, url=LICENSE_URL)
LICENSE_NOTICE_HTML = '<p>%s</p>' % LICENSE_NOTICE.replace('\n\n', '</p><p>')
LICENSE_NOTICE_HTML = re.sub(r'<http([^>]*)>', r'<a href="http\1" target="_blank">http\1</a>',
    LICENSE_NOTICE_HTML)

if __name__ == '__main__':
  setup(**SETUP)
