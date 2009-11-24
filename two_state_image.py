#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Image that defaults back to a default state after a while.

You can switch the image to something else but it defaults back to the default
image (the first image) after calling EmptyEvent() a few times
"""

__author__ = 'scott@forusers.com (Scott Kirkwood))'

import pygtk
pygtk.require('2.0')
import gtk

class TwoStateImage(gtk.Image):
  def __init__(self, pixbufs, normal, show=True):
    gtk.Image.__init__(self)
    self.pixbufs = pixbufs
    self.normal = normal
    self.count_down = None
    self.showit = show
    self.SwitchTo(self.normal)

  def SwitchTo(self, name):
    self.count_down = 3
    self._SwitchTo(name)

  def _SwitchTo(self, name):
    self.set_from_pixbuf(self.pixbufs.Get(name))
    if self.showit:
      self.show()

  def SwitchToDefault(self):
    self._SwitchTo(self.normal)
    self.count_down = None

  def EmptyEvent(self):
    if not self.count_down:
      return
    self.count_down -= 1
    if self.count_down == 0:
      self.SwitchToDefault()
