#!/usr/bin/python
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

"""Options Class for save, restoring and getting parameters from the command line.

This provides a class which handles both saving options to disk and gathering
options from the command line.

It behaves a little like optparse in that you can get or set the attributes by
name.

It uses ConfigParser to save the variables to disk in ini format.
"""
__author__ = 'Scott Kirkwood (scott+keymon@forusers.com)'

import ConfigParser
import gettext
import logging
import optparse
import os

LOG = logging.getLogger('options')

gettext.install('key-mon', 'locale')

class OptionException(Exception):
  pass

class OptionItem(object):
  """Handles on option.
  It know both about optparse options and ConfigParser options.
  By setting opt_short, opt_long to None you won't create an optparse option.
  By setting ini_group, ini_name to None you won't create a ConfigParser option.
  """
  def __init__(self, dest, _type, default, name, help,
      opt_group=None, opt_short=None, opt_long=None,
      ini_group=None, ini_name=None):
    """Create an option
    Args:
      dest: a unique name for this variable, used internally.
      _type: The data type.
      default: The default value if none given.
      name: the translated name.
      _help: Help text to show.
      opt_group: Optional option group
      opt_short: the short name of the option
      opt_long: the long name for the option
      ini_group: optional name of the group in the ini file.
      ini_name: optional name of the name in the ini file
    """
    self._dirty = False
    self._value = None
    self._temp_value = None

    self._dest = dest
    self._type = _type
    self._default = default
    self._name = name
    self._help = help
    self._opt_group = opt_group
    self._opt_short = opt_short
    if self._opt_short and not self._opt_short.startswith('-'):
      raise OptionException('Invalid short option %s' % self._opt_short)
    self._opt_long = opt_long
    if self._opt_long and not self._opt_long.startswith('--'):
      raise OptionException('Invalid long option %r' % self._opt_long)
    self._ini_group = ini_group
    self._ini_name = ini_name
    if self._type not in ('int', 'float', 'bool', 'str'):
      raise OptionException('Unsupported type: %s' % self._type)
    self._set_value(default)

  def add_to_parser(self, parser):
    if not self._opt_short and not self._opt_long:
      return
    if self._type == 'bool':
      self._add_bool_to_parser(parser)
      return
    args = []
    if self._opt_short:
      args.append(self._opt_short)
    if self._opt_long:
      args.append(self._opt_long)
    parser.add_option(dest=self._dest, type=self._type, default=self._default,
       help=self._help, *args)

  def _add_bool_to_parser(self, parser):
    """Booleans need special handling."""
    args = []
    if self._opt_short:
      args.append(self._opt_short)
    if self._opt_long:
      args.append(self._opt_long)
    parser.add_option(action='store_true', default=self._default,
      dest=self._dest, help=self._help, *args)

    if self._ini_group:
      # Only need the --no version if it could be saved to ini file.
      parser.add_option('--no' + self._opt_long.lstrip('-'),
              action='store_false',
              dest=self._dest, help=_('Opposite of %s') % self._opt_long)

  def set_from_optparse(self, opts):
    """Try and set an option from optparse.
    Args:
      opts: options as returned from parse_args()
    """
    if not self._opt_short and not self._opt_long:
      return
    if hasattr(opts, self._dest):
      opt_val = getattr(opts, self._dest)
      if not self._ini_name:
        # For commands like --version which aren't stored
        self._set_value(opt_val)
      self._set_temp_value(opt_val)

  def reset_to_default(self):
    """Reset to the default value."""
    self._set_value(self._default)
    self._set_temp_value(None)

  def get_value(self):
    """Return the value."""
    if self._temp_value is not None:
      return self._temp_value
    return self._value

  def _set_attr_value(self, attr, val):
    """Set the value via attribute name.
    Args:
      attr: attribute name ('_value', or '_temp_value')
      val: value to set
    """
    old_val = getattr(self, attr)
    if val is None:
      setattr(self, attr, val)
    elif self._type == 'int':
      setattr(self, attr, int(val))
    elif self._type == 'float':
      setattr(self, attr, float(val))
    elif self._type == 'bool':
      if isinstance(val, basestring):
        if val.lower() in ('false', 'off', 'no', '0'):
          setattr(self, attr, False)
        elif val.lower() in ('true', 'on', 'yes', '1'):
          setattr(self, attr, True)
        else:
          raise OptionException('Unable to convert %s to bool' % val)
      else:
        setattr(self, attr, bool(val))
    else:
      setattr(self, attr, val)
    self._dirty = old_val != getattr(self, attr)
    if self._dirty and self._temp_value:
      self._temp_value = None

  def _set_value(self, val):
    self._set_attr_value('_value', val)
    self._set_attr_value('_temp_value', None)

  def _set_temp_value(self, val):
    self._set_attr_value('_temp_value', val)

  value = property(get_value, _set_value, doc="Value")

  @property
  def dest(self):
    """Destination variable name."""
    return self._dest

  @property
  def name(self):
    """Localized name of the option."""
    return self._name

  @property
  def help(self):
    """Long description of the option."""
    return self._help

  @property
  def type(self):
    """String name of the type."""
    return self._type

  @property
  def opt_group(self):
    """Option group, if any."""
    return self._opt_group

  @property
  def opt_short(self):
    """Short option property (ex. '-v')."""
    return self._opt_short

  @property
  def opt_long(self):
    """Long option property (ex. '--verbose')."""
    return self._opt_long

  @property
  def ini_group(self):
    """Name of the ini group or None."""
    return self._ini_group

  @property
  def ini_name(self):
    """Name in the ini, or None."""
    return self._ini_name

  @property
  def ini_value(self):
    """Value to store in the ini, always a string."""
    if self._value is None:
      return None
    if self._type == 'bool':
      if self._value is True:
        return '1'
      else:
        return '0'
    else:
      return str(self._value)


class Options(object):
  """Store the options in memory, also saves to dist and creates opt_parser."""
  def __init__(self):
    self._options = {}
    self._ini_filename = None
    self._opt_group = None
    self._opt_group_desc = {}
    self._options_order = []

  def __getattr__(self, name):
    if name not in self.__dict__['_options']:
      raise AttributeError('Invalid attribute name: %r' % name)
    return self._options[name].value

  def __setattr__(self, name, value):
    if name == '_options' or name not in self.__dict__['_options']:
      object.__setattr__(self, name, value)
    else:
      LOG.info('Setting %r = %r', name, value)
      self.__dict__['_options'][name].value = value

  def add_option_group(self, group, desc):
    self._opt_group = group
    self._opt_group_desc[group] = desc

  def add_option(self, dest, type='str', default=None, name=None, help=None,
      opt_short=None, opt_long=None,
      ini_group=None, ini_name=None):
    """Create an option
    Args:
      dest: a unique name for this variable, used internally.
      type: The data type.
      default: The default value if none given.
      name: the translated name.
      help: Help text to show.
      opt_group: the name of the option group or None
      opt_short: the short name of the option
      opt_long: the long name for the option
      ini_group: the name of the group in the ini file.
      ini_name: the name of the name in the ini file
    """
    if dest in self._options:
      raise OptionException('Options %s already added' % dest)

    self._options_order.append(dest)
    self._options[dest] = OptionItem(dest, type, default,
        name, help,
        opt_group=self._opt_group, opt_short=opt_short, opt_long=opt_long,
        ini_group=ini_group, ini_name=ini_name)

  def parse_args(self, desc, args=None):
    """Add the options to the optparse instance and parse command line
    Args:
      desc: Description to use for the program.
      args: Args for testing or sys.args[1:] otherwise
    """
    parser = optparse.OptionParser(desc)
    for dest in self._options_order:
      opt = self._options[dest]
      opt.add_to_parser(parser)

    self._opt_ret, self._other_args = parser.parse_args(args)
    for opt in self._options.values():
      opt.set_from_optparse(self._opt_ret)

  def parse_ini(self, fp):
    """Parser an ini file from fp, which is file-like class."""

    config = ConfigParser.SafeConfigParser()
    config.readfp(fp)
    checker = {}
    for opt in self._options.values():
      if opt.ini_group:
        checker[opt.ini_group + '-' + opt.ini_name] = True
        if (config.has_section(opt.ini_group) and
            config.has_option(opt.ini_group, opt.ini_name)):
          opt.value = config.get(opt.ini_group, opt.ini_name)
          LOG.info('From ini getting %s.%s = %s', opt.ini_group, opt.ini_name,
              opt.value)
    for section in config.sections():
      for name, value in config.items(section):
        combined_name = section + '-' + name
        if not combined_name in checker:
          LOG.info('Unknown option %r in section [%s]', name, section)
          # we no longer throw an error to be backward compatible

  def write_ini(self, fp):
    """Parser an ini file from fp, which is file-like class."""

    config = ConfigParser.SafeConfigParser()
    for opt in self._options.values():
      if not opt.ini_group:
        continue
      if not config.has_section(opt.ini_group):
        config.add_section(opt.ini_group)

      if opt.ini_value is not None:
        config.set(opt.ini_group, opt.ini_name, opt.ini_value)
    config.write(fp)

  def read_ini_file(self, fname):
    self._ini_filename = os.path.expanduser(fname)
    LOG.info('Reading from %r', self._ini_filename)
    if os.path.exists(self._ini_filename) and os.path.isfile(self._ini_filename):
      fi = open(self._ini_filename)
      self.parse_ini(fi)
      fi.close()
    else:
      LOG.info('%r does not exist', self._ini_filename)

  def save(self):
    self._write_ini_file(self._ini_filename)

  def _make_dirs(self, fname):
    if not os.path.exists(fname):
      dirname = os.path.dirname(fname)
      if not os.path.exists(dirname):
        LOG.info('Creating directory %r', dirname)
        os.makedirs(dirname)

  def _write_ini_file(self, fname):
    self._make_dirs(fname)
    LOG.info('Writing config file %r', fname)
    fo = open(fname, 'w')
    self.write_ini(fo)
    fo.close()

  def reset_to_defaults(self):
    """Reset ini file to defaults."""
    for opt in self._options.values():
      if not opt.ini_group:
        continue
      opt.reset_to_default()

if __name__ == '__main__':
  o = Options()
  o.add_option(opt_short='-l', opt_long='--larger', dest='larger', default=False,
               type='bool',
               help='Make the dialog 25% larger than normal.')
  o.add_option(opt_short='-m', opt_long='--meta', dest='meta', type='bool',
               ini_group='buttons', ini_name='meta', default=False,
               help='Show the meta (windows) key.')
  o.add_option(opt_long='--scale', dest='scale', type='float', default=1.0,
               ini_group='ui', ini_name='scale',
               help='Scale the dialog. ex. 2.0 is 2 times larger, 0.5 is '
                    'half the size. Defaults to %default')
  o.add_option(opt_long='--kbdfile', dest='kbd_file',
               ini_group='devices', ini_name='map',
               default='us.kbd',
               help='Use this kbd filename instead running xmodmap.')
  o.add_option(opt_short='-v', opt_long='--version', dest='version', type='bool',
               help='Show version information and exit.')
  o.add_option(opt_short='-t', opt_long='--theme', dest='theme', type='str',
               ini_group='ui', ini_name='theme',
               help='The theme to use when drawing status images (ex. "-t apple").')
  o.add_option(opt_long='--list-themes', dest='list_themes', type='bool',
               help='List available themes')
  o.add_option(opt_long='--old-keys', dest='old_keys', type='int',
               ini_group='buttons', ini_name='old-keys',
               help='How many historical keypresses to show (defaults to %default)',
               default=0)
  o.add_option(opt_short=None, opt_long=None, type='int',
               dest='x_pos', default=-1, help='Last X Position',
               ini_group='position', ini_name='x')
  o.add_option_group('Developer Options', 'Don\'t use')
  o.add_option(opt_short='-d',
               opt_long='--debug', dest='debug', type='bool',
               help='Output debugging information.')
  lines = []
  lines.append('[ui]')
  lines.append('scale = 1.0')
  lines.append('theme = classic')
  lines.append('[buttons]')
  lines.append('meta = 0')
  lines.append('old-keys = 0')
  lines.append('[devices]')
  lines.append('map = us.kbd')
  lines.append('[position]')
  lines.append('x = -1')
  import StringIO
  io = StringIO.StringIO('\n'.join(lines))
  o.parse_ini(io)
  o.parse_args('%prog [options]')
  io = StringIO.StringIO()
  o.write_ini(io)
  print io.getvalue()
