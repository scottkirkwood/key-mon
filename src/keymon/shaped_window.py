#!/usr/bin/python
#
# Copyright 2010 Scott Kirkwood. All Rights Reserved.

"""Create a shaped window to show mouse events.

Thanks to mathias.gumz for the original code.

"""
import cairo
import gtk
import math

class ShapedWindow(gtk.Window):
  def __init__(self):
    gtk.Window.__init__(self)
    self.connect('size-allocate', self._OnSizeAllocate)
    self.set_decorated(False)

  def _OnSizeAllocate(self, win, allocation):
    w, h = allocation.width, allocation.height
    bitmap = gtk.gdk.Pixmap(None, w, h, 1)
    cr = bitmap.cairo_create()

    # Clear the bitmap
    cr.set_source_rgb(0.0, 0.0, 0.0)
    cr.set_operator(cairo.OPERATOR_CLEAR)
    cr.paint()

    # Draw our shape into the bitmap using cairo
    cr.set_source_rgb(1.0, 1.0, 1.0)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.arc(w / 2, h / 2, min(h, w) / 2, 0, 2 * math.pi)
    cr.fill()

    # Set the window shape
    win.shape_combine_mask(bitmap, 0, 0)
