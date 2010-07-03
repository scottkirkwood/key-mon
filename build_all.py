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

import os
import sys
import re
from pybdist import pybdist
import setup
import shutil
import subprocess

def BuildScreenShots():
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
    ('old-keys-2', ['--noctrl', '--noalt', '--nomouse', '--old-keys', '2'], ['KEY_Y', 'KEY_Y', 'KEY_P']),
  ]
  for fname, options, keys in todos:
    pybdist.KillConfig()
    subprocess.call([
      'python', prog] + options + ['--screenshot', ','.join(keys)])
    shutil.move('screenshot.png', os.path.join(destdir, fname + '.png'))
  pybdist.KillConfig()


def CopyDir(from_dir, to_dir):
  """Recursively copy all the files from `from_dir` and below to `to_dir`."""
  print 'Copying from %r to %r' % (from_dir, to_dir)
  os.makedirs(to_dir)
  for fname in os.listdir(from_dir):
    from_name = os.path.join(from_dir, fname)
    if os.path.isdir(from_name):
      CopyDir(from_name, os.path.join(to_dir, fname))
    else:
      shutil.copy2(from_name, to_dir)

def MoveTopFilesToDir(from_dir, to_dir):
  """Copy top level files (only) in `from_dir` to `to_dir`."""
  os.makedirs(to_dir)
  for fname in os.listdir(from_dir):
    from_name = os.path.join(from_dir, fname)
    if os.path.isfile(from_name):
      shutil.move(from_name, to_dir)
  print 'Moved files to %r' % to_dir

def BuildDeb(setup):
  tmpdir = 'tmp'
  shutil.rmtree(tmpdir, True)
  dest_dir = '%s-%s' % (setup.NAME, setup.VER)
  dest_tar = '%s_%s' % (setup.NAME, setup.VER)
  CopyDir('debian', os.path.join(tmpdir, dest_dir, 'debian'))

  src_tarname = dest_dir + '.tar.gz'
  dest_tarname = dest_tar + '.tar.gz'
  os.symlink(os.path.abspath(os.path.join('dist', src_tarname)),
             os.path.abspath(os.path.join(tmpdir, dest_tarname)))

  dest_tarname = dest_tar + '.orig.tar.gz'
  os.symlink(os.path.abspath(os.path.join('dist', src_tarname)),
             os.path.abspath(os.path.join(tmpdir, dest_tarname)))

  args = ['tar', '-zx', '--directory', tmpdir, '-f', os.path.join('dist', dest_dir + '.tar.gz')]
  print ' '.join(args)
  ret = subprocess.call(args)
  if ret:
    print 'Error untarring file'
    sys.exit(-1)
  old_cwd = os.getcwd()
  os.chdir(os.path.join(tmpdir, dest_dir))
  args = ['debuild',
      '--lintian-opts', '--info', '--display-info', '--display-experimental',
      '--color', 'always',
      #'--pedantic'
      #'--fail-on-warnings',
      ]
  print ' '.join(args)
  ret = subprocess.call(args)
  if ret:
    print 'Error running debuild'
    sys.exit(-1)
  os.chdir(old_cwd)
  # Move
  if os.path.exists('/etc/debian_version'):
    deb_ver = open('/etc/debian_version').read().rstrip()
  else:
    deb_ver = 'UNKNOWN'
  debdir='debian-%s' % deb_ver
  shutil.rmtree(debdir, True)
  MoveTopFilesToDir(tmpdir, debdir)

  # Cleanup
  shutil.rmtree(tmpdir, True)


if __name__ == '__main__':
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('--clean', dest='doclean', action='store_true',
                    help='Uninstall things')
  parser.add_option('--png', dest='png', action='store_true',
                    help='Only build png files')
  parser.add_option('--pypi', dest='pypi', action='store_true',
                    help='Only upload to pypi')
  parser.add_option('--freshmeat', dest='freshmeat', action='store_true',
                    help='Announce on freshmeat')
  parser.add_option('--dist', dest='dist', action='store_true',
                    help='Only build distributions.')
  parser.add_option('--upload', dest='upload', action='store_true',
                    help='Only upload to google code.')
  parser.add_option('--all', dest='all', action='store_true',
                    help='Do everything')
  (options, args) = parser.parse_args()
  ver = pybdist.GetVersion(setup)
  rel_date, rel_lines = pybdist.ParseLastRelease(setup)
  print 'Version is %r, date %r' % (ver, rel_date)
  print 'Release notes'
  print '-------------'
  print '\n'.join(rel_lines)
  print

  if options.png:
    BuildScreenShots()
  elif options.doclean:
    pybdist.CleanAll(setup)
  elif options.dist:
    pybdist.BuildMan(setup)
    pybdist.BuildZipTar(setup)
    BuildDeb(setup)
  elif options.upload:
    pybdist.UploadToGoogleCode(setup)
  elif options.pypi:
    pybdist.UploadToPyPi(setup)
  elif options.freshmeat:
    pybdist.AnnounceOnFreshmeat(setup)
  elif options.twitter:
    pybdist.AnnounceOnTwitter(setup)
  elif options.all:
    BuildScreenShots()
    pybdist.BuildMan(setup)
    pybdist.BuildZipTar(setup)
    BuildDeb(setup)
    pybdist.UploadToGoogleCode(setup)
    pybdist.UploadToPyPi(setup)
    pybdist.AnnounceOnFreshmeat(setup)
  else:
    print 'Doing nothing.  --help for commands.'
