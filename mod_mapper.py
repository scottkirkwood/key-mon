#!/usr/bin/python
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Run mod map and convert to something I can use."""

__author__ = 'scott@forusers.com (scottkirkwood)'

import codecs
import subprocess
import re

MEDIUM_NAME = {
  'REDO': 'Redo',
  'ESCAPE': 'Esc',
  'MINUS': '-',
  'EQUAL': '=',
  'BACKSPACE': 'Back',
  'TAB': 'Tab',
  'BRACKETLEFT': '[',
  'BRACKETRIGHT': ']',
  'RETURN': 'Return',
  'CONTROL_L': 'Control',
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
  'NUM_LOCK': 'NumLock',
  'SCROLL_LOCK': 'ScrollLock',
  'KP_HOME': 'Home',
  'KP_UP': '\u2191',
  'KP_PRIOR': u'\u2190',
  'KP_SUBTRACT': '-',
  'KP_LEFT': u'\u2190',
  'KP_BEGIN': 'Begin',
  'KP_RIGHT': u'\u2192',
  'KP_ADD': 'Add',
  'KP_END': 'End',
  'KP_DOWN': u'\u2193',
  'KP_NEXT': 'Next',
  'KP_INSERT': 'Insert',
  'KP_DELETE': 'Delete',
  'ISO_LEVEL3_SHIFT': 'L3 Shift',
  'LESS': '<',
  'KP_ENTER': 'Enter',
  'CONTROL_R': 'Control',
  'KP_DIVIDE': '/',
  'PRINT': 'Print',
  'ISO_LEVEL3_SHIFT': 'L3 Shift',
  'LINEFEED': 'Lf',
  'HOME': 'Home',
  'UP': '\u2191',
  'PRIOR': 'Prior',
  'LEFT': u'\u2190',
  'RIGHT': u'\u2192',
  'END': 'End',
  'DOWN': u'\u2193',
  'NEXT': 'Next',
  'INSERT': 'Insert',
  'DELETE': 'Delete',
  'XF86AUDIOMUTE': 'Mute',
  'XF86AUDIOLOWERVOLUME': 'Vol+',
  'XF86AUDIORAISEVOLUME': 'Vol-',
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
  'XF86WAKEUP': 'Wakeup',
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
  'XF86BACK': u'\u21fd',
  'XF86FORWARD': 'Forward',
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
  'CONTROL_L': 'Ctrl',
  'SHIFT_L': 'Shft',
  'SHIFT_R': 'Shft',
  'SPACE': 'Spc',
  'MULTI_KEY': 'Mul',
  'NUM_LOCK': 'Num',
  'SCROLL_LOCK': 'SLck',
  'KP_HOME': 'Hm',
  'KP_DOWN': 'Dn',
  'KP_INSERT': 'Ins',
  'KP_DELETE': 'Del',
  'ISO_LEVEL3_SHIFT': 'Shft',
  'KP_ENTER': u'\u23CE',
  'CONTROL_R': 'Ctrl',
  'PRINT': 'Prt',
  'ISO_LEVEL3_SHIFT': 'Shft',
  'LINEFEED': 'Lf',
  'HOME': 'Hm',
  'INSERT': 'Ins',
  'DELETE': 'Del',
  'XF86AUDIOMUTE': 'Mute',
  'XF86AUDIOLOWERVOLUME': 'V-',
  'XF86AUDIORAISEVOLUME': 'V+',
  'XF86POWEROFF': 'Off',
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
  return ParseKdb(codecs.open(fname, 'r', 'utf-8').read())

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
  default = 'us.kdb'
  if fname:
    return ReadKdb(fname)
  ret = None
  try:
    ret = ReadModMap()
    if ret:
      return ret
  except:
    print 'Error: unable execute xmodmap, reading default %r' % fname
  return ReadKdb(default)


if __name__ == '__main__':
  fname = 'my.kdb'
  modmap = ReadModMap()
  CreateMykdb(fname, modmap)
  entries = ReadKdb(fname)
  print 'Read %r with %d entires' % (fname, len(entries))
  for code in modmap:
    if code not in entries:
      print 'Missing entry for code %s' % code
