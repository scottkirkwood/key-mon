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
    """Get the pixbuf with this name."""
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
      logging.error('Don\'t understand the name %r', name)
      return 'KEY_EMPTY'
    ops = self.name_fnames[name]
    img = None
    for op in ops:
      if isinstance(op, types.StringTypes):
        img = self._Composite(img, self._ReadFromFile(op))
      else:
        image_bytes = op()
        image_bytes = self._Resize(image_bytes)
        img = self._Composite(img, self._ReadFromBytes(image_bytes))
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
    """Read in the file in from fname."""
    logging.debug('Read file %s', fname)
    if self.resize == 1.0:
      return gtk.gdk.pixbuf_new_from_file(fname)
    fi = open(fname)
    image_bytes = self._Resize(fi.read())
    fi.close()
    return self._ReadFromBytes(image_bytes)

  def _ReadFromBytes(self, image_bytes):
    """Writes the bytes to a file and then reads the file."""
    fo, fname = tempfile.mkstemp(prefix='keymon-', suffix='.svg')
    os.write(fo, image_bytes)
    os.close(fo)
    try:
      img = gtk.gdk.pixbuf_new_from_file(fname)
    except:
      logging.error('Unable to read %r: %s', fname, image_bytes)
      sys.exit(-1)

    try:
      os.unlink(fname)
    except OSError:
      pass
    return img

  def _Resize(self, image_bytes):
    """Resize the image by manipulating the svg."""
    if self.resize == 1.0:
      return image_bytes
    template = r'(<svg[^<]+)(%s=")(\d+\.?\d*)'
    image_bytes = self._ResizeText(image_bytes, template % 'width')
    image_bytes = self._ResizeText(image_bytes, template % 'height')
    image_bytes = image_bytes.replace('<g',
        '<g transform="scale(%f, %f)"' % (self.resize, self.resize), 1)
    return image_bytes

  def _ResizeText(self, image_bytes, regular_exp):
    """Change the numeric value of some sizing text by regular expression."""
    re_x = re.compile(regular_exp)
    grps = re_x.search(image_bytes)
    if grps:
      num = float(grps.group(3))
      num = num * self.resize
      replace = grps.group(1) + grps.group(2) + str(num)
      image_bytes = re_x.sub(replace, image_bytes, 1)
    return image_bytes
