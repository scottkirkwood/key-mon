#!/usr/bin/python
import re

def ParseLastRelease(fname):
  """Parse the last release in an RST release file.
  Args:
    fname: filename
  Returns:
    (version, date, lines)
  """
  # Example "Apr. 18th, 2009 v 0.16"
  re_version = re.compile(r'(.*) v (\d+.\d+(?:.\d+)?)$')
  re_horz = re.compile(r'^[-=]+$')
  version = None
  lines = []
  for line in open(fname):
    line = line.rstrip()
    grps = re_version.match(line)
    if grps:
      if version:
        break;
      date, version = grps.group(1), grps.group(2)
    elif re_horz.match(line):
      pass
    elif version:
      lines.append(line)

  if not lines[-1]:
    del lines[-1]

  return version, date, lines

def RstExperiment():
  import docutils
  import docutils.utils
  from docutils.parsers.rst import Parser
  from docutils import core

  fname = 'RELEASE.rst'
  overrides = {'input_encoding': 'unicode',
               'doctitle_xform': 1,
               'initial_header_level': 1}
  lines = []
  for line in open(fname):
    lines.append(unicode(line))

  document = core.publish_doctree(
      source=u'\n'.join(lines), source_path=fname,
      settings_overrides=overrides)

  parts = core.publish_parts(
      source=u'\n'.join(lines), source_path=fname,
      destination_path=None,
      writer_name='html', settings_overrides=overrides)
  body = parts['html_body']
  print body

if __name__ == '__main__':
  ver, date, lines = ParseLastRelease('RELEASE.rst')
  print ver, date, lines
