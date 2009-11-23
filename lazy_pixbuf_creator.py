#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Create pixbuf on demand.

This creates a gtk pixbuf in one of three manners:
1) Simple filename (probably supports most image formats)
2) Multiple filenames composted together (last one on top).
3) Image is given to a function passed as bytes for the program to returned modified.
"""

__author__ = 'scott@forusers.com (Scott Kirkwood))'

import pygtk
pygtk.require('2.0')
import gtk
import types
import tempfile

import logging

class LazyPixbufCreator():
  """Class to create SVG images on the fly."""
  def __init__(self, name_fnames):
    """Initialize with empty.
    
    Args:
      name_fnames: List of names to filename list.
    """
    self.pixbufs = {}
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
      return 'KEY_UP_EMPTY'
    print 'Creating %s' % name
    ops = self.name_fnames[name]
    if len(ops) == 1:
      self.pixbufs[name] = gtk.gdk.pixbuf_new_from_file(ops[0])
    elif len(ops) == 2 and isinstance(ops[1], types.StringTypes):
      img1 = gtk.gdk.pixbuf_new_from_file(ops[1])
      img2 = gtk.gdk.pixbuf_new_from_file(ops[0])
      img1.composite(img2, 
          0, 0, img1.props.width, img1.props.height,  # x, y, w, h
          0, 0,  # offset x, y
          1.0, 1.0,  # scale x, y
          gtk.gdk.INTERP_HYPER, 255)  # interpolation type, alpha
      self.pixbufs[name] = img2
    elif len(ops) == 2:
      print 'Convert by function'
      fun = ops[1]
      bytes = open(ops[0]).read()
      bytes = fun(bytes)
      f = tempfile.NamedTemporaryFile(mode='w', prefix='keymon-', delete=True)
      f.write(bytes)
      f.flush()
      self.pixbufs[name] = gtk.gdk.pixbuf_new_from_file(f.name)
      f.close()

    return name

