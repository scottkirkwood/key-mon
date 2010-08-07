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

class LazyPixbufCreator(object):
  """Class to create SVG images on the fly."""
  def __init__(self, name_fnames, resize):
    """Initialize with empty.

    Args:
      name_fnames: List of names to filename list.
    """
    self.pixbufs = {}
    self.resize = resize
    self.name_fnames = name_fnames

  def reset_all(self, names_fnames, resize):
    """Resets the name to filenames and size."""
    self.pixbufs = {}
    self.name_fnames = names_fnames
    self.resize = resize

  def get(self, name):
    """Get the pixbuf with this name."""
    if name not in self.pixbufs:
      name = self.create_pixbuf(name)
    return self.pixbufs[name]

  def create_pixbuf(self, name):
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
    for operation in ops:
      if isinstance(operation, types.StringTypes):
        img = self._composite(img, self._read_from_file(operation))
      else:
        image_bytes = operation()
        image_bytes = self._resize(image_bytes)
        img = self._composite(img, self._read_from_bytes(image_bytes))
    self.pixbufs[name] = img
    return name

  def _composite(self, img, img2):
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

  def _read_from_file(self, fname):
    """Read in the file in from fname."""
    logging.debug('Read file %s', fname)
    if self.resize == 1.0:
      return gtk.gdk.pixbuf_new_from_file(fname)
    fin = open(fname)
    image_bytes = self._resize(fin.read())
    fin.close()
    return self._read_from_bytes(image_bytes)

  def _read_from_bytes(self, image_bytes):
    """Writes the bytes to a file and then reads the file."""
    fout, fname = tempfile.mkstemp(prefix='keymon-', suffix='.svg')
    os.write(fout, image_bytes)
    os.close(fout)
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

  def _resize(self, image_bytes):
    """Resize the image by manipulating the svg."""
    if self.resize == 1.0:
      return image_bytes
    template = r'(<svg[^<]+)(%s=")(\d+\.?\d*)'
    image_bytes = self._resize_text(image_bytes, template % 'width')
    image_bytes = self._resize_text(image_bytes, template % 'height')
    image_bytes = image_bytes.replace('<g',
        '<g transform="scale(%f, %f)"' % (self.resize, self.resize), 1)
    return image_bytes

  def _resize_text(self, image_bytes, regular_exp):
    """Change the numeric value of some sizing text by regular expression."""
    re_x = re.compile(regular_exp)
    grps = re_x.search(image_bytes)
    if grps:
      num = float(grps.group(3))
      num = num * self.resize
      replace = grps.group(1) + grps.group(2) + str(num)
      image_bytes = re_x.sub(replace, image_bytes, 1)
    return image_bytes
