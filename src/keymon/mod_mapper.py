#!/usr/bin/python
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Run mod map and convert to something I can use."""

__author__ = 'scott@forusers.com (scottkirkwood)'

import codecs
import os
import re
import subprocess
import sys

MEDIUM_NAME = {
  'REDO': 'Redo',
  'ESCAPE': 'Esc',
  'PLUS': '+',
  'MINUS': '-',
  'EQUAL': '=',
  'BACKSPACE': 'Back',
  'TAB': 'Tab',
  'BRACKETLEFT': '[',
  'BRACKETRIGHT': ']',
  'BRACELEFT': '(',
  'BRACERIGHT': ')',
  'DEAD_ACUTE': u'\u00B4',
  'ACUTE': u'\u00B4',
  'QUESTIONDOWN': u'\u00BF',
  'WAKEUP': 'Wake',
  'BAR': '|',
  'TILDE': '~',
  'NTILDE': '~',
  'RETURN': 'Return',
  'CONTROL_L': 'Ctrl',
  'SEMICOLON': ';',
  'APOSTROPHE': '\'',
  'GRAVE': '`',
  'SHIFT_L': 'Shift',
  'BACKSLASH': '\\',
  'COMMA': ',',
  'PERIOD': '.',
  'SLASH': '/',
  'SHIFT_R': 'Shift',
  'KP_MULTIPLY': '*',
  'ALT_L': 'Alt',
  'SPACE': 'Space',
  'MULTI_KEY': 'Multi',
  'NUM_LOCK': 'Num',
  'SCROLL_LOCK': 'Scrl',
  'KP_HOME': '7',
  'KP_UP': '8',
  'KP_PRIOR': '9',
  'KP_SUBTRACT': '-',
  'KP_LEFT': '4',
  'KP_BEGIN': '5',
  'KP_RIGHT': '6',
  'KP_ADD': '+',
  'KP_END': '1',
  'KP_DOWN': '2',
  'KP_NEXT': '3',
  'KP_INSERT': '0',
  'KP_DELETE': '.',
  'ISO_LEVEL3_SHIFT': 'Alt',  # Right Alt
  'LESS': '<',
  'KP_ENTER': u'\u23CE',
  'CONTROL_R': 'Ctrl',
  'KP_DIVIDE': '/',
  'PRINT': 'Print',
  'LINEFEED': 'Lf',
  'HOME': 'Home',
  'UP': u'\u2191',
  'PRIOR': 'PgUp',
  'LEFT': u'\u2190',
  'RIGHT': u'\u2192',
  'END': 'End',
  'DOWN': u'\u2193',
  'NEXT': 'PgDn',
  'INSERT': 'Ins',
  'DELETE': 'Del',
  'XF86AUDIOMUTE': 'Mute',
  'XF86AUDIOLOWERVOLUME': 'Vol-',
  'XF86AUDIORAISEVOLUME': 'Vol+',
  'XF86POWEROFF': 'Off',
  'KP_EQUAL': '=',
  'PLUSMINUS': '+/-',
  'PAUSE': 'Pause',
  'KP_DECIMAL': '.',
  'SUPER_L': 'Super',
  'MULTI_KEY': 'Multi',
  'MENU': 'Menu',
  'CANCEL': 'Cancel',
  'REDO': 'Redo',
  'SUNPROPS': 'Sunprops',
  'UNDO': 'Undo',
  'SUNFRONT': 'Sunfront',
  'XF86COPY': 'Copy',
  'SUNOPEN': 'SunOpen',
  'XF86PASTE': 'Paste',
  'FIND': 'Find',
  'XF86CUT': 'Cut',
  'HELP': 'Help',
  'XF86MENUKB': 'MenuKb',
  'XF86CALCULATOR': 'Calc',
  'XF86SLEEP': 'Sleep',
  'XF86WAKEUP': 'Wake',
  'XF86EXPLORER': 'Explorer',
  'XF86SEND': 'Send',
  'XF86XFER': 'Xfer',
  'XF86LAUNCH1': 'Launch1',
  'XF86LAUNCH2': 'Launch2',
  'XF86WWW': 'www',
  'XF86DOS': 'Dos',
  'XF86SCREENSAVER': 'Screensaver',
  'XF86ROTATEWINDOWS': 'RotateWin',
  'XF86MAIL': 'Mail',
  'XF86FAVORITES': 'Fav',
  'XF86MYCOMPUTER': 'MyComputer',
  'XF86BACK': u'\u21d0',
  'XF86FORWARD': u'\u21d2',
  'XF86EJECT': 'Eject',
  'XF86AUDIONEXT': 'Next',
  'XF86AUDIOPLAY': 'Play',
  'XF86AUDIOPREV': 'Prev',
  'XF86AUDIOSTOP': 'Stop',
  'XF86AUDIORECORD': 'Record',
  'XF86AUDIOREWIND': 'Rewind',
  'XF86PHONE': 'Phone',
  'XF86TOOLS': 'Tools',
  'XF86HOMEPAGE': 'HomePage',
  'XF86RELOAD': 'Reload',
  'XF86CLOSE': 'Close',
  'XF86SCROLLUP': 'ScrollUp',
  'XF86SCROLLDOWN': 'ScrollDn',
  'PARENLEFT': '(',
  'PARENRIGHT': ')',
  'XF86NEW': 'New',
  'REDO': 'Redo',
  'MODE_SWITCH': 'Mode',
  'NOSYMBOL': '-',
  'XF86AUDIOPLAY': 'Play',
  'XF86AUDIOPAUSE': 'Pause',
  'XF86LAUNCH3': 'Launch3',
  'XF86LAUNCH4': 'Launch4',
  'XF86SUSPEND': 'Suspend',
  'XF86CLOSE': 'Close',
  'XF86WEBCAM': 'WebCam',
  'XF86MAIL': 'Mail',
  'XF86SEARCH': 'Search',
  'XF86FINANCE': 'Finance',
  'XF86SHOP': 'Shop',
  'CANCEL': 'Cancel',
  'XF86MONBRIGHTNESSDOWN': 'BrightnessDown',
  'XF86MONBRIGHTNESSUP': 'BrightnessUp',
  'XF86AUDIOMEDIA': 'AudioMedia',
  'XF86DISPLAY': 'Display',
  'XF86KBDLIGHTONOFF': 'LightOnOff',
  'XF86KBDBRIGHTNESSDOWN': 'BrightnessDown',
  'XF86KBDBRIGHTNESSUP': 'BrightnessUp',
  'XF86SEND': 'Send',
  'XF86REPLY': 'Reply',
  'XF86MAILFORWARD': 'MailForward',
  'XF86SAVE': 'Save',
  'XF86DOCUMENTS': 'Docs',
  'XF86BATTERY': 'Battery',
  'XF86BLUETOOTH': 'Bluetooth',
  'XF86WLAN': 'Lan',
}

SHORT_NAME = {
  'BACKSPACE': u'\u21fd',
  'RETURN': u'\u23CE',
  'CONTROL_L': 'Ctl',
  'SHIFT_L': 'Shft',
  'SHIFT_R': 'Shft',
  'SPACE': 'Spc',
  'MULTI_KEY': 'Mul',
  'PRINT': 'Prt',
  'LINEFEED': 'Lf',
  'HOME': 'Hm',
  'INSERT': 'Ins',
  'DELETE': 'Del',
  'XF86AUDIOMUTE': 'Mute',
  'XF86AUDIOLOWERVOLUME': 'V-',
  'XF86AUDIORAISEVOLUME': 'V+',
  'XF86POWEROFF': 'Off',
  'PRIOR': 'PgU',
  'NEXT': 'PgD',
  'PAUSE': 'Ps',
  'SUPER_L': 'Spr',
  'MULTI_KEY': 'Mul',
  'MENU': 'Men',
  'CANCEL': 'Can',
  'REDO': 'Red',
  'UNDO': 'Und',
  'XF86COPY': 'Cp',
  'XF86CUT': 'Cut',
  'XF86MENUKB': 'MenuKb',
}


def mod_map_args():
  return ['xmodmap', '-display', ':0', '-pk']


def run_cmd(args):
  """Run the command and collect the output."""
  return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]


def parse_modmap(lines):
  re_range = re.compile(r'KeyCodes range from (\d+) to')
  lower_bound = 8
  re_line = re.compile(r'^\s+(\d+)\s+0x[\dA-Fa-f]+\s+(.*)')
  re_remainder = re.compile(r'\((.+?)\)')
  ret = {}
  for line in lines.split('\n'):
    if not line:
      continue
    grps = re_range.search(line)
    if grps:
      lower_bound = int(grps.group(1))
    grps = re_line.search(line)
    if grps:
      code = int(grps.group(1)) - lower_bound
      str = []
      for grp in re_remainder.finditer(grps.group(2)):
        str.append(grp.group(1))

      # We'll pick the first one
      alias = str[0].upper()
      my_keyname = 'KEY_' + alias
      my_keyname = my_keyname.replace('XF86', '')
      ret[code] = (my_keyname, alias)
  return ret


def ReadKdb(fname):
  return ParseKdb(codecs.open(os.path.join(os.path.dirname(__file__), fname),
                              'r', 'utf-8').read())


def ParseKdb(text):
  re_line = re.compile(r'(\d+) (\S+) (\S+)\s?(\S*)')
  ret = {}
  for line in text.split('\n'):
    if not line:
      continue
    grps = re_line.search(line)
    if grps:
      ret[int(grps.group(1))] = (grps.group(2), grps.group(3), grps.group(4))
  return ret


def CreateMykdb(fname, codes):
  f = codecs.open(fname, 'w', 'utf-8')
  f.write('# This is a space separated file with UTF-8 encoding\n')
  f.write('# Short name is optional, will default to the medium-name\n')
  f.write('# Scancode Map-Name Medium-Name Short-Name\n')
  for code, (key, medium_name, short_name) in codes.items():
    if short_name:
      f.write('%d %s %s %s\n' % (code, key, medium_name, short_name))
    else:
      f.write('%d %s %s\n' % (code, key, medium_name))
  print 'Output %r with %d entries' % (fname, len(codes))
  f.close()


def ReadModMap():
  xmodmap = parse_modmap(run_cmd(mod_map_args()))
  ret = {}
  for code in xmodmap:
    key = xmodmap[code][0]
    key_name = xmodmap[code][1]
    if key_name in MEDIUM_NAME:
      medium_name = MEDIUM_NAME[key_name]
    else:
      medium_name = key_name
    if key_name in SHORT_NAME:
      short_name = SHORT_NAME[key_name]
    else:
      short_name = None
    ret[code] = (key, medium_name, short_name)
  return ret


def SafelyReadModMap(fname):
  pathname = os.path.dirname(__file__)
  default = 'us.kbd'
  if fname:
    if os.path.exists(fname):
      return ReadKdb(fname)
    else:
      return ReadKdb(os.path.join(pathname, fname))
  ret = None
  try:
    ret = ReadModMap()
  except:
    print 'Error: unable execute xmodmap, reading default %r' % fname
  defaults = ReadKdb(os.path.join(pathname, default))
  if not ret:
    return defaults
  # Merge the defaults with modmap
  for keycode in defaults:
    if keycode not in ret:
      ret[keycode] = defaults[keycode]
  return ret


if __name__ == '__main__':
  fname = 'my.kdb'
  modmap = ReadModMap()
  CreateMykdb(fname, modmap)
  entries = ReadKdb(fname)
  print 'Read %r with %d entires' % (fname, len(entries))
  for code in modmap:
    if code not in entries:
      print 'Missing entry for code %s' % code
