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
import gettext


NAME = 'key-mon'
DIR = 'src/keymon'
gettext.install(NAME, DIR + '/locale')
VER = '1.9'
PY_NAME = 'key_mon'
DEB_NAME = NAME.replace('-', '')
RELEASE_FILE = 'RELEASE.rst'
VCS = 'http://%s.code.google.com/hg' % NAME

PY_SRC = '%s.py' % PY_NAME
DEPENDS = ['python-xlib', 'python-gtk2']
DEPENDS_STR = ' '.join(DEPENDS)

MENU_SUBSECTION = 'Graphics'
AUTHOR_NAME = 'Scott Kirkwood'
COPYRIGHT_NAME = 'Google Inc.'
GOOGLE_CODE_EMAIL = 'scott@forusers.com'
MAILING_LIST = 'key-mon-discuss@googlegroups.com'
KEYWORDS = ['keyboard', 'status', 'monitor', 'education']
MAN_FILE = 'man/%s.1' % NAME
DESKTOP_FILE = 'icons/%s.desktop' % NAME
ICON = 'icons/%s.xpm' % NAME
COMMAND = '/usr/bin/%s' % NAME
LANGS = ['pt_BR']

SETUP = dict(
  name=NAME,
  version=VER,
  packages=['keymon'],
  package_dir={
      'keymon': 'src/keymon'},
  package_data = {
      'keymon': [
          'themes/**/*', '*.kbd',
          'icons/key-mon.desktop', 'locale/**/*/*.mo'],
  },
  data_files = [
      ('share/pixmaps', [ICON]),
  ],
  scripts=['src/key-mon'],
  author=AUTHOR_NAME,
  author_email='scott+keymon@forusers.com',
  platforms=['POSIX'],
  license='Apache 2.0',
  keywords=' '.join(KEYWORDS),
  url='http://code.google.com/p/%s' % NAME,
  download_url='http://%s.googlecode.com/files/%s-%s.zip' % (NAME, NAME, VER),
  description=_('A screencast utility that displays your keyboard and mouse status'),
  long_description=_("""Key-mon is useful for teaching since it shows the current status of your
keyboard and mouse and you use them in another application.  No longer do you need to say
'Now I'm pressing the Ctrl-D key', your students can just see the keystroke for themselves."""),
  classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: X11 Applications',
      'Intended Audience :: Education',
      'License :: OSI Approved :: Apache Software License',
      'Operating System :: POSIX :: Linux',
      'Topic :: Education :: Computer Aided Instruction (CAI)',
  ],
)

if __name__ == '__main__':
  setup(**SETUP)
