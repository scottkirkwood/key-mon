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

import logging
import os
import ConfigParser
import optparse

LOG = logging.getLogger('options')

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
    parser.add_option(*args,
       dest=self._dest, type=self._type, default=self._default,
       help=self._help)

  def _add_bool_to_parser(self, parser):
    """Booleans need special handling."""
    args = []
    if self._opt_short:
      args.append(self._opt_short)
    if self._opt_long:
      args.append(self._opt_long)
    parser.add_option(*args, action='store_true', default=self._default,
      dest=self._dest, help=self._help)

    parser.add_option('--no' + self._opt_long.lstrip('-'), action='store_false',
      dest=self._dest)

  def set_from_optparse(self, opts):
    """Try and set an option from optparse.
    Args:
      opts: options as returned from parse_args()
    """
    if not self._opt_short and not self._opt_long:
      return
    if hasattr(opts, self._dest):
      self._set_value(getattr(opts, self._dest))

  @property
  def value(self):
    """Return the value."""
    return self._value

  @value.setter
  def value(self, val):
    self._set_value(val)

  def _set_value(self, val):
    old_val = self._value
    if val is None:
      self._value = val
    elif self._type == 'int':
      self._value = int(val)
    elif self._type == 'float':
      self._value = float(val)
    elif self._type == 'bool':
      if isinstance(val, basestring):
        if val.lower() in ('false', 'off', 'no', '0'):
          self._value = False
        elif val.lower() in ('true', 'on', 'yes', '1'):
          self._value = True
        else:
          raise OptionException('Unable to convert %s to bool' % val)
      else:
        self._value = bool(val)
    else:
      self._value = val
    self._dirty = old_val != self._value

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
    self.opt_group = None
    self.options_order = []
    self.options = {}

  def __getattr__(self, name):
    if name not in self.options:
      raise OptionException('Invalidate `dest` name: %r' % name)
    return self.options[name].value

  def add_option_group(self, group, desc):
    self.opt_group = group

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
    if dest in self.options:
      raise OptionException('Options %s already added' % dest)

    self.options_order.append(dest)
    self.options[dest] = OptionItem(dest, type, default,
        name, help,
        opt_group=self.opt_group, opt_short=opt_short, opt_long=opt_long,
        ini_group=ini_group, ini_name=ini_name)

  def parse_args(self, args=None):
    """Add the options to the optparse instance and parse command line
    Args:
      args: Args for testing or sys.args[1:] otherwise
    """
    parser = optparse.OptionParser()
    for dest in self.options_order:
      opt = self.options[dest]
      opt.add_to_parser(parser)

    self.opt_ret, self.other_args = parser.parse_args(args)
    for opt in self.options.values():
      opt.set_from_optparse(self.opt_ret)

  def parse_ini(self, fp):
    """Parser an ini file from fp, which is file-like class."""

    config = ConfigParser.SafeConfigParser()
    config.readfp(fp)
    for opt in self.options.values():
      if opt.ini_group:
        if (config.has_section(opt.ini_group) and
            config.has_option(opt.ini_group, opt.ini_name)):
          opt.value = config.get(opt.ini_group, opt.ini_name)
          LOG.info('From ini getting %s.%s = %s', opt.ini_group, opt.ini_name,
              opt.value)

  def write_ini(self, fp):
    """Parser an ini file from fp, which is file-like class."""

    config = ConfigParser.SafeConfigParser()
    for opt in self.options.values():
      if not opt.ini_group:
        continue
      if not config.has_section(opt.ini_group):
        config.add_section(opt.ini_group)

      if opt.ini_value is not None:
        config.set(opt.ini_group, opt.ini_name, opt.ini_value)
    config.write(fp)

  def write_ini_file(self, fname):
    if not os.path.exists(fname):
      dirname = os.path.dirname(fname)
      if not os.path.exists(dirname):
        LOG.info('Creating directory %r', dirname)
        os.makedirs(dirname)
    fo = file(fname, 'w')
    LOG.info('Writing config file %r', fname)
    write_ini(fo)
    fo.close()

if __name__ == '__main__':
  o = Options()
  o.add_option(opt_short='-s', opt_long='--smaller', dest='smaller', default=False,
               type='bool',
               help='Make the dialog 25% smaller than normal.')
  o.add_option(opt_short='-l', opt_long='--larger', dest='larger', default=False,
               type='bool',
               help='Make the dialog 25% larger than normal.')
  o.add_option(opt_short='-m', opt_long='--meta', dest='meta', type='bool',
               default=False,
               help='Show the meta (windows) key.')
  o.add_option(opt_long='--mouse', dest='mouse', type='bool', default=True,
               ini_group='buttons', ini_name='mouse',
               help='Show the mouse.')
  o.add_option(opt_long='--shift', dest='shift', type='bool', default=True,
               ini_group='buttons', ini_name='shift',
               help='Show shift key.')
  o.add_option(opt_long='--ctrl', dest='ctrl', type='bool', default=True,
               ini_group='buttons', ini_name='ctrl',
               help='Show the ctrl key.')
  o.add_option(opt_long='--alt', dest='alt', type='bool', default=True,
               ini_group='buttons', ini_name='alt',
               help='Show the alt key.')
  o.add_option(opt_long='--scale', dest='scale', type='float', default=1.0,
               ini_group='buttons', ini_name='scale',
               help='Scale the dialog. ex. 2.0 is 2 times larger, 0.5 is '
                    'half the size. Defaults to %default')
  o.add_option(opt_long='--decorated', dest='decorated', type='bool',
               ini_group='ui', ini_name='decorated',
               default=True,
               help='Show decoration')
  o.add_option(opt_long='--visible_click', dest='visible_click', type='bool',
               ini_group='ui', ini_name='visible_click',
               default=False,
               help='Show where you clicked')
  o.add_option(opt_long='--kbdfile', dest='kbd_file',
               ini_group='devices', ini_name='map',
               default='us.kbd',
               help='Use this kbd filename instead running xmodmap.')
  o.add_option(opt_long='--swap', dest='swap_buttons', type='bool',
               default=False,
               ini_group='devices', ini_name='swap_buttons',
               help='Swap the mouse buttons.')
  o.add_option(opt_long='--emulate-middle', dest='emulate_middle', type='bool',
               default=False,
               ini_group='devices', ini_name='emulate_middle',
               help='When you press the left, and right mouse buttons at the same time, '
                    'it displays as a middle mouse button click. ')
  o.add_option(opt_short='-v', opt_long='--version', dest='version', type='bool',
               help='Show version information and exit.')
  o.add_option(opt_short='-t', opt_long='--theme', dest='theme', type='str',
               ini_group='ui', ini_name='theme',
               help='The theme to use when drawing status images (ex. "-t apple").')
  o.add_option(opt_long='--list-themes', dest='list_themes', type='bool',
               help='List available themes')
  o.add_option(opt_long='--old-keys', dest='old_keys', type='int',
               help='How many historical keypresses to show (defaults to %default)',
               default=0)

  o.add_option_group('Developer Options', 'Don\'t use')
  o.add_option(opt_short='-d',
               opt_long='--debug', dest='debug', type='bool',
               help='Output debugging information.')
  o.add_option(opt_long='--screenshot', dest='screenshot', type='bool', default=False,
               help='Create a "screenshot.png" and exit. '
                    'Pass a comma separated list of keys to simulate (ex. "KEY_A,KEY_LEFTCTRL").')

  lines = []
  lines.append('[ui]')
  lines.append('decorated = 0')
  lines.append('opacity = 0.9')
  lines.append('scale = 1.0')
  lines.append('theme = classic')
  lines.append('visible-click = 0')
  lines.append('[buttons]')
  lines.append('mouse = 1')
  lines.append('shift = 1')
  lines.append('ctrl = 1')
  lines.append('alt = 1')
  lines.append('meta = 0')
  lines.append('old-keys = 0')
  lines.append('[devices]')
  lines.append('map = us.kbd')
  lines.append('emulate_middle = 0')
  lines.append('swap_buttons = 0')
  lines.append('[position]')
  lines.append('x = -1')
  lines.append('y = -1')
  import StringIO
  io = StringIO.StringIO('\n'.join(lines))
  o.parse_ini(io)
  o.parse_args()
  io = StringIO.StringIO()
  o.write_ini(io)
  print io.getvalue()