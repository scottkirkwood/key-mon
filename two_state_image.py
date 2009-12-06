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
import time

TIMEOUT_SECS = 0.2

class TwoStateImage(gtk.Image):
  def __init__(self, pixbufs, normal, show=True):
    gtk.Image.__init__(self)
    self.pixbufs = pixbufs
    self.normal = normal
    self.count_down = None
    self.showit = show
    self.current = ''
    self.SwitchTo(self.normal)

  def SwitchTo(self, name):
    # reset the time
    if self.current != name:
      self._SwitchTo(name)

  def _SwitchTo(self, name):
    self.set_from_pixbuf(self.pixbufs.Get(name))
    self.current = name
    if self.showit:
      self.show()

  def SwitchToDefault(self):
    self.count_down = time.time()

  def EmptyEvent(self):
    if self.count_down is None:
      return
    delta = time.time() - self.count_down
    if delta > TIMEOUT_SECS:
      self.count_down = None
      self._SwitchTo(self.normal)
