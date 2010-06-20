#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.
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
    pybdist.BuildDeb(setup)
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
    pybdist.BuildDeb(setup)
    pybdist.UploadToGoogleCode(setup)
    pybdist.UploadToPyPi(setup)
    pybdist.AnnounceOnFreshmeat(setup)
  else:
    print 'Doing nothing.  --help for commands.'
