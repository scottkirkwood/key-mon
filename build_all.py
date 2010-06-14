#!/usr/bin/python
"""
Build everything for keymon.

* Build the man pages.
* Create the screen shots.
* Build the debian package.
* Build the zip file via setup.py sdist

You'll need:
sudo aptitude install alien help2man fakeroot
"""
import getpass
import os
import re
import shutil
import subprocess
import sys

def GetVersion(fname):
  re_py_ver = re.compile(r'__version__\s*=\s*[\'"](.*)[\'"]')
  grps = re_py_ver.search(open(fname).read())
  source_ver = grps.group(1)

  fname = 'setup.py'
  re_setup_ver = re.compile(r'VER=\'(.*)\'')
  grps = re_setup_ver.search(open(fname).read())
  setup_ver = grps.group(1)
  if setup_ver == source_ver:
    print 'Setup versions agree'
  else:
    print 'Setup versions dissagree'
    print 'key_mon.py = %r' % source_ver
    print 'setup.py = %r' % setup_ver
    print 'Please fix this before continuing'
    sys.exit(-1)

  return setup_ver


def BuildZip():
  subprocess.call([
    'python', 'setup.py', 'sdist', '--formats=zip'])
  print 'Built zip'


def BuildMan():
  try:
    subprocess.call([
      'help2man',
      'src/keymon/key_mon.py',
      '-i', 'man/key-mon.include',
      '-o', 'man/key-mon.1'])
    print 'Built key-mon.1'
  except Exception, e:
    print 'You may need to install help2man', e
    sys.exit(-1)


def BuildDeb(ver):
  subprocess.call([
    'python', 'setup.py', 'bdist_rpm',])
  rpm_file = 'key-mon-%s-1.noarch.rpm' % ver
  print 'Converting %s to .deb' % rpm_file
  old_cwd = os.getcwd()
  os.chdir('dist')
  try:
    ret = subprocess.call([
      'fakeroot', 'alien', rpm_file])
    if ret:
      print 'You may need to install fakeroot and/or alien'
      print 'Failed to build debian package'
      sys.exit(-1)
      return
  except Exception, e:
    print 'You may need to install fakeroot and/or alien', e
    os.chdir(old_cwd)
    sys.exit(-1)
  os.chdir(old_cwd)
  print 'Built debian package'


def KillConfig():
  config_file = os.path.expanduser('~/.config/key-mon/config')
  if os.path.exists(config_file):
    os.unlink(config_file)


def BuildScreenShots():
  prog = 'src/keymon/key_mon.py'
  destdir = 'docs'
  all_buttons = ['KEY_A', 'KEY_LEFTCTRL', 'KEY_LEFTALT', 'KEY_LEFTSHIFT']
  todos = [
    ('screenshot', [], all_buttons),
    ('screenshot-blank', [], ['KEY_EMPTY']),
    ('screenshot-smaller', ['--smaller'], all_buttons),
    ('screenshot-larger', ['--larger'], all_buttons),
    ('screenshot-apple', ['--theme', 'apple'], all_buttons),
    ('screenshot-oblivion', ['--theme', 'oblivion'], all_buttons),
    ('screenshot-modern', ['--theme', 'modern'], all_buttons),
    ('2x-no-mouse-meta', ['--nomouse', '--scale', '2.0', '--meta'], all_buttons + ['KEY_LEFTMETA']),
    ('old-keys-2', ['--nomouse', '--old-keys', '2'], ['KEY_Y', 'KEY_Y', 'KEY_P']),
  ]
  for fname, options, keys in todos:
    KillConfig()
    subprocess.call([
      'python', prog] + options + ['--screenshot', ','.join(keys)])
    shutil.move('screenshot.png', os.path.join(destdir, fname + '.png'))
  KillConfig()


def UploadFile(fname, username, password):
  import googlecode_upload as gup
  project = 'key-mon'
  print 'Uploading %s' % fname
  gup.upload('dist/%s' % fname, project, username, password, fname)
  print 'Done.'


def UploadFiles(ver):
  username = 'scott@forusers.com'
 
  print 'Using user %r' % username
  # Read password if not loaded from svn config, or on subsequent tries.
  print 'Please enter your googlecode.com password.'
  print '** Note that this is NOT your Gmail account password! **'
  print 'It is the password you use to access repositories,'
  print 'and can be found here: http://code.google.com/hosting/settings'
  password = getpass.getpass()
  UploadFile('key-mon-%s.zip' % ver, username, password)
  UploadFile('key-mon-%s.tar.gz' % ver, username, password)
  UploadFile('key-mon_%s-2_all.deb' % ver, username, password)


if __name__ == '__main__':
  ver = GetVersion('src/keymon/key_mon.py')
  print 'Version is %r' % ver
  BuildScreenShots()
  BuildMan()
  BuildDeb(ver)
  BuildZip()
  #UploadFiles(ver)
  # TODO upload to PyPi
