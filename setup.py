#!/usr/bin/env python3
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
VER = '1.20'
PY_NAME = 'key_mon'
DEB_NAME = NAME.replace('-', '')
RELEASE_FILE = 'RELEASE.rst'
VCS = 'https://github.com/scottkirkwood/key-mon.git'

PY_SRC = f'{PY_NAME}.py'
DEPENDS = ['python3-xlib', 'python3-gi-cairo', 'gir1.2-gtk-3.0']
DEPENDS_STR = ' '.join(DEPENDS)

MENU_SUBSECTION = 'Graphics'
AUTHOR_NAME = 'Scott Kirkwood'
COPYRIGHT_NAME = 'Google Inc.'
GOOGLE_CODE_EMAIL = 'scott@forusers.com'
MAILING_LIST = 'key-mon-discuss@googlegroups.com'
KEYWORDS = ['keyboard', 'status', 'monitor', 'education']
MAN_HELP = f'src/{NAME}'
MAN_FILE = f'man/{NAME}.1'
DESKTOP_FILE = f'icons/{NAME}.desktop'
ICON = f'icons/{NAME}.xpm'
COMMAND = f'/usr/bin/{NAME}'
LANGS = []
HICOLOR_PNG_SIZES = [16, 24, 32, 48, 64, 128]

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
      ('share/icons/hicolor', [f'icons/hicolor/{x}x{x}/apps/{NAME}.png' for x in HICOLOR_PNG_SIZES]),
      ('share/icons/hicolor', [f'icons/hicolor/scalable/apps/{NAME}.svg']),
  ],
  scripts=['src/key-mon'],
  author=AUTHOR_NAME,
  author_email='scott+keymon@forusers.com',
  platforms=['POSIX'],
  license='Apache 2.0',
  keywords=' '.join(KEYWORDS),
  url='https://github.com/scottkirkwood/key-mon',
  download_url=f'https://github.com/scottkirkwood/{NAME}/archive/{VER}.zip',
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
