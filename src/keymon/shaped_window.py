#!/usr/bin/python
#
# Copyright 2010 Scott Kirkwood. All Rights Reserved.

"""Create a shaped window to show mouse events.

Thanks to mathias.gumz for the original code.

"""
import gobject
import gtk
import math

import lazy_pixbuf_creator

class ShapedWindow(gtk.Window):
  def __init__(self, fname, scale=1.0):
    gtk.Window.__init__(self)
    self.connect('size-allocate', self._OnSizeAllocate)
    self.set_decorated(False)
    self.set_keep_above(True)
    self.scale = scale
    self.name_fnames = {
      'mouse' : [fname],
    }
    self.pixbufs = lazy_pixbuf_creator.LazyPixbufCreator(self.name_fnames,
                                                         self.scale)
    self.pixbuf = self.pixbufs.Get('mouse')
    self.resize(self.pixbuf.get_width(), self.pixbuf.get_height())

    # a pixmap widget to contain the pixmap
    self.image = gtk.Image()
    bitmap, self.mask = self.pixbuf.render_pixmap_and_mask()
    self.image.set_from_pixmap(bitmap, self.mask)
    self.image.show()
    self.add(self.image)

  def _OnSizeAllocate(self, win, allocation):
    w, h = allocation.width, allocation.height
    # Set the window shape
    win.shape_combine_mask(self.mask, 0, 0)
    win.set_property('skip-taskbar-hint', True)
    if not win.is_composited():
      print 'Unable to fade the window'
    else:
      win.set_opacity(0.5)

  def FadeAway(self):
    self.present()
    gobject.timeout_add(200, self.hide)
