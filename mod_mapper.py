#!/usr/bin/python
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Run mod map and convert to something I can use."""

__author__ = 'scott@forusers.com (scottkirkwood)'

import subprocess
import re

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
      xmodname = str[0]
      xmodname = 'KEY_' + xmodname.upper()
      xmodname = xmodname.replace('XF86', '')
      ret[code] = xmodname
  return ret

def parse_kdb(text):
  re_line = re.compile(r'(\d+) (.+)')
  re_hex_line = re.compile(r'(0x[A-Fa-f\d]+) (.+)')
  ret = {}
  for line in text.split('\n'):
    if not line:
      continue
    grps = re_line.search(line)
    if grps:
      ret[int(grps.group(1))] = grps.group(2)
      continue
    grps = re_hex_line.search(line)
    if grps:
      ret[int(grps.group(1), 16)] = grps.group(2)

  return ret

def run():
  codes = parse_kdb(open('us.kbd').read())
  xmodmap = parse_modmap(run_cmd(mod_map_args()))
  for key in codes:
    if key in xmodmap:
      name = codes[key]
      xmodname = xmodmap[key]
      if name != xmodname:
        print '%s = %s' % (name, xmodname)

if __name__ == '__main__':
  run()
