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

import codecs
import getpass
import glob
import httplib
import setup
import netrc
import os
import re
import release
import shutil
import simplejson
import subprocess
import sys

def GetVersion(fname):
  re_py_ver = re.compile(r'__version__\s*=\s*[\'"](.*)[\'"]')
  grps = re_py_ver.search(open(fname).read())
  source_ver = grps.group(1)

  setup_ver = setup.VER
  if setup_ver == source_ver:
    print 'Setup versions agree'
  else:
    print 'Setup versions dissagree'
    print '%s = %r' % (setup.PY_SRC, source_ver)
    print 'setup.py = %r' % setup_ver
    print 'Please fix this before continuing'
    sys.exit(-1)

  return setup_ver


def BuildZipTar():
  subprocess.call([
    'python', 'setup.py', 'sdist', '--formats=gztar,zip'])
  print 'Built zip'


def UploadToPyPi():
  subprocess.call([
    'python', 'setup.py', 'sdist', '--formats=zip', 'upload',])
  print 'Upload to pypi'


def BuildMan():
  try:
    dest_dir = 'man'
    dest_name = '%s/%s.1' % (dest_dir, setup.NAME)
    if not os.path.isdir(dest_dir):
      os.makedirs(dest_dir)
    subprocess.call([
      'help2man',
      '%s/%s' % (setup.DIR, setup.PY_SRC),
      #'%s' % setup.NAME,
      '-N', # no pointer to TextInfo
      '-i', 'man/%s.include' % setup.NAME,
      '-o', dest_name])

    print 'Built %s.1' % setup.NAME
  except Exception, e:
    print 'You may need to install help2man', e
    sys.exit(-1)


def BuildDeb(ver):
  import distutils.core
  import build_deb
  sys.argv = [sys.argv[0], 'bdist_deb', '--sdist=dist/%s-%s.tar.gz' % (setup.NAME, ver)]
  setup.SETUP.update(dict(
      cmdclass={'bdist_deb': build_deb.bdist_deb},
      options=dict(
        bdist_deb=dict(
          package=setup.DEB_NAME,
          title=setup.NAME,
          description=setup.SETUP['description'],
          long_description=setup.SETUP['long_description'],
          version=ver,
          author=setup.AUTHOR_NAME,
          author_email=setup.SETUP['author_email'],
          copyright=setup.COPYRIGHT,
          license=setup.LICENSE_TITLE_AND_VERSION,
          license_abbrev=setup.LICENSE_TITLE_AND_VERSION_ABBREV,
          license_path='/usr/share/common-licenses/GPL-3',
          license_summary=setup.LICENSE_NOTICE,
          subsection=setup.MENU_SUBSECTION,
          depends='python-xlib',
          url=setup.SETUP['url'],
          man_src='man/%s.1' % setup.SETUP['name'],
          command='/usr/bin/'))))
  distutils.core.setup(**setup.SETUP)
  GetDebFilenames(ver)
  print 'Built debian package'
  return


def GetDebFilenames(ver):
  debs = ['dist/%s_%s-1_all.deb' % (setup.DEB_NAME, ver)]
  for deb in debs:
    if not os.path.exists(deb):
      print 'Missing debian file %s' % deb
      sys.exit(-1)

  return debs


def KillConfig():
  config_file = os.path.expanduser('~/.config/%s/config' % setup.NAME)
  if os.path.exists(config_file):
    os.unlink(config_file)

def CleanAll():
  KillConfig()
  dist_dir = '/usr/local/lib/python2.6/dist-packages'
  dist_packages = '%s/%s' % (dist_dir, os.path.basename(setup.DIR))
  if os.path.exists(dist_packages):
    print 'rm -r %s' % dist_packages
    shutil.rmtree(dist_packages)
  dist_egg = '%s/%s-*.egg-info' % (dist_dir, setup.PY_NAME)
  for fname in glob.glob(dist_egg):
    if os.path.exists(fname):
      if os.path.isdir(fname):
        print 'rm -r %s' % fname
        shutil.rmtree(fname)
      else:
        print 'rm %s' % fname
        os.unlink(fname)
  docs = '/usr/share/doc/%s' % setup.NAME
  if os.path.exists(docs):
    print 'rm -r %s' % docs
    shutil.rmtree(docs)

  for script in setup.SETUP['scripts']:
    bin_script = '/usr/local/bin/%s' % os.path.basename(script)
    if os.path.exists(bin_script):
      print 'rm %s' % bin_script
      os.unlink(bin_script)

def BuildScreenShots():
  prog = '%s/%s' % (setup.DIR, setup.PY_SRC)
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
  project = setup.NAME
  print 'Uploading %s' % fname
  summary = fname
  if fname.endswith('.zip') or fname.endswith('.tar.gz'):
    labels = ['Type-Source', 'OpSys-Linux']
  elif fname.endswith('.deb'):
    summary += ' (python 2.6)'
    labels = ['Type-Package', 'OpSys-Linux']
  else:
    labels = None
  gup.upload('dist/%s' % fname, project, username, password, summary, labels)
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
  UploadFile('%s-%s.zip' % (setup.NAME, ver), username, password)
  UploadFile('%s-%s.tar.gz' % (setup.NAME, ver), username, password)
  for deb in GetDebFilenames(ver):
    UploadFile(deb.replace('dist/', ''), username, password)


def AnnounceOnFreshmeat(ver, lines):
  """Announce launch on freshmeat.
  Args:
    vers: the version string
    lines: the lines from the release notes.
  """
  print 'Announcing on Freshmeat...'
  rc = netrc.netrc(os.path.expanduser('~/.netrc'))
  # Storing the auth_code as the account in the .netrc file
  # ex. chmod 600 ~/.netrc
  # machine freshmeat
  #     login myname
  #     account auth_code_given_by_freshmeat
  #     password mypassword
  auth_code = rc.authenticators('freshmeat')[1]
  name = setup.NAME
  tag = 'Bug fixes'
  if ver.endswith('.0'):
    tag = 'Feature enhancements'
  changelog = ['Changes: '] + lines
  release = dict(version=ver, changelog='\n'.join(changelog), tag_list=tag)
  path = '/projects/%s/releases.json' % name
  body = codecs.encode(simplejson.dumps(dict(auth_code=auth_code, release=release)))
  connection = httplib.HTTPConnection('freshmeat.net')
  connection.request('POST', path, body, {'Content-Type': 'application/json'})
  response = connection.getresponse()
  if response.status != 201:
    print 'Request failed: %d %s' % (response.status, response.reason)
  print 'Done announcing on Freshmeat.'

def DoPyPi():
  UploadToPyPi()

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
  fname = '%s/%s' % (setup.DIR, setup.PY_SRC)
  ver = GetVersion(fname)
  rel_fname = 'docs/RELEASE.rst'
  rel_ver, rel_date, rel_lines = release.ParseLastRelease(rel_fname)
  if rel_ver != ver:
    print 'Need to update the %r, version %r doesn\'t match %r' % (rel_fname, rel_ver, ver)
    sys.exit(-1)
  print 'Version is %r, date %r' % (ver, rel_date)
  print 'Release notes'
  print '-------------'
  print '\n'.join(rel_lines)
  print

  if options.png:
    BuildScreenShots()
  elif options.doclean:
    CleanAll()
  elif options.dist:
    BuildMan()
    BuildZipTar()
    BuildDeb(ver)
  elif options.upload:
    UploadFiles(ver)
  elif options.pypi:
    DoPyPi()
  elif options.freshmeat:
    AnnounceOnFreshmeat(ver, rel_lines)
  elif options.all:
    BuildScreenShots()
    BuildMan()
    BuildZipTar()
    BuildDeb(ver)
    UploadFiles(ver)
    DoPyPi()
    AnnounceOnFreshmeat(ver, rel_lines)
  else:
    print 'Doing nothing.  --help for commands.'
