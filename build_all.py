#!/usr/bin/python
# -*- coding: utf-8 -*-
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

"""
Build everything for keymon.

* Build the man pages.
* Create the screen shots.
* Build the debian package.
* Build the zip file via setup.py sdist

You'll need:
sudo apt-get install alien help2man fakeroot lintian
Also pip pybdist
"""

from pybdist import pybdist
import optparse
import os
import setup
import shutil
import subprocess

def build_screen_shots():
  """Build the screenshots for key-mon."""
  prog = '%s/%s' % (setup.DIR, setup.PY_SRC)
  destdir = 'docs'
  all_buttons = ['KEY_A', 'KEY_CONTROL_L', 'KEY_ALT_L', 'KEY_SHIFT_L']
  todos = [
    ('screenshot', [], all_buttons + ['BTN_LEFT']),
    ('screenshot-blank', [], ['KEY_EMPTY']),
    ('screenshot-smaller', ['--smaller'], all_buttons + ['BTN_LEFT']),
    ('screenshot-larger', ['--larger'], all_buttons + ['BTN_LEFT']),
    ('screenshot-apple', ['--theme', 'apple'], all_buttons + ['BTN_RIGHT']),
    ('screenshot-oblivion', ['--theme', 'oblivion'], all_buttons + ['BTN_LEFT']),
    ('screenshot-modern', ['--theme', 'modern'], all_buttons + ['BTN_LEFT']),
    ('2x-no-mouse-meta', ['--nomouse', '--scale', '2.0', '--meta'], all_buttons + ['KEY_SUPER_L']),
    ('old-keys-2', ['--noctrl', '--noalt', '--nomouse', '--old-keys', '2'],
        ['KEY_Y', 'KEY_Y', 'KEY_P']),
  ]
  for fname, options, keys in todos:
    pybdist.clean_config(setup)
    subprocess.call([
      'python', prog] + options + ['--screenshot', ','.join(keys)])
    shutil.move('screenshot.png', os.path.join(destdir, fname + '.png'))
  pybdist.clean_config(setup)


def main():
  """Run the program, put here to make linter happy."""
  parser = optparse.OptionParser()
  parser.add_option('--png', dest='png', action='store_true',
                    help='Only build png files')
  pybdist.add_standard_options(parser)
  (options, unused_args) = parser.parse_args()
  pybdist.get_and_verify_versions(setup)

  if options.png:
    build_screen_shots()
  elif not pybdist.handle_standard_options(options, setup):
    print 'Doing nothing.  --help for commands.'

if __name__ == '__main__':
  main()
