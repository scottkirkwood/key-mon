#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Create pixbuf on demand.

This creates a gtk pixbuf in one of 2 manners:
1) Simple filename (probably supports most image formats)
2) A function which returns bytes to a file which can be read by
   pixbuf_new_from_file().

The name_fnames contains a list for key.  Each element of the list will be
composted with the previous element (overlayed on top of).

Alpha transparencies from the new, overlayed, image are respected.
"""

__author__ = 'scott@forusers.com (Scott Kirkwood))'

import pygtk
pygtk.require('2.0')
import gtk
import logging
import os
import sys
import re
import tempfile
import types

class LazyPixbufCreator():
  """Class to create SVG images on the fly."""
  def __init__(self, name_fnames, resize):
    """Initialize with empty.

    Args:
      name_fnames: List of names to filename list.
    """
    self.pixbufs = {}
    self.resize = resize
    self.name_fnames = name_fnames

  def Get(self, name):
    if name not in self.pixbufs:
      name = self.CreatePixbuf(name)
    return self.pixbufs[name]

  def CreatePixbuf(self, name):
    """Creates the image.
    Args:
      name: name of the image we are to create.
    Returns:
      The name given or EMPTY if error.
    """
    if name not in self.name_fnames:
      logging.error('Don\'t understand the name %r' % name)
      return 'KEY_EMPTY'
    ops = self.name_fnames[name]
    img = None
    for op in ops:
      if isinstance(op, types.StringTypes):
        img = self._Composite(img, self._ReadFromFile(op))
      else:
        bytes = op()
        bytes = self._Resize(bytes)
        img = self._Composite(img, self._ReadFromBytes(bytes))
    self.pixbufs[name] = img
    return name

  def _Composite(self, img, img2):
    """Combine/layer img2 on top of img.
    Args:
      img: original image (or None).
      img2: new image to add on top.
    Returns:
      updated image.
    """
    if img:
      img2.composite(img,
          0, 0, img.props.width, img.props.height,  # x, y, w, h
          0, 0,  # offset x, y
          1.0, 1.0,  # scale x, y
          gtk.gdk.INTERP_HYPER, 255)  # interpolation type, alpha
      return img
    return img2

  def _ReadFromFile(self, fname):
    logging.debug('Read file %s' % fname)
    if self.resize == 1.0:
      return gtk.gdk.pixbuf_new_from_file(fname)
    f = open(fname)
    bytes = self._Resize(f.read())
    f.close()
    return self._ReadFromBytes(bytes)


  def _ReadFromBytes(self, bytes):
    """Writes the bytes to a file and then reads the file."""
    f, fname = tempfile.mkstemp(prefix='keymon-', suffix='.svg')
    os.write(f, bytes)
    os.close(f)
    try:
      img = gtk.gdk.pixbuf_new_from_file(fname)
    except:
      logging.error('Unable to read %r: %s' % (fname, bytes))
      sys.exit(-1)
    try:
      os.unlink(fname)
    except OSError:
      pass
    return img

  def _Resize(self, bytes):
    if self.resize == 1.0:
      return bytes
    template = r'(<svg[^<]+)(%s=")(\d+\.?\d*)'
    bytes = self._ResizeText(bytes, template % 'width')
    bytes = self._ResizeText(bytes, template % 'height')
    bytes = bytes.replace('<g',
        '<g transform="scale(%f, %f)"' % (self.resize, self.resize), 1)
    return bytes

  def _ResizeText(self, bytes, regular_exp):
    re_x = re.compile(regular_exp)
    grps = re_x.search(bytes)
    if grps:
      num = float(grps.group(3))
      num = num * self.resize
      replace = grps.group(1) + grps.group(2) + str(num)
      bytes = re_x.sub(replace, bytes, 1)
    return bytes
