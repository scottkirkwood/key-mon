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

"""Create a shaped window to show mouse events.

Thanks to mathias.gumz for the original code.
"""
import gobject
import gtk

import lazy_pixbuf_creator

class ShapedWindow(gtk.Window):
  """Create a window shaped as fname."""
  def __init__(self, fname, scale=1.0):
    gtk.Window.__init__(self)
    self.connect('size-allocate', self._on_size_allocate)
    self.set_decorated(False)
    self.set_keep_above(True)
    self.scale = scale
    self.is_shown = False
    self.name_fnames = {
      'mouse' : [fname],
    }
    self.pixbufs = lazy_pixbuf_creator.LazyPixbufCreator(self.name_fnames,
                                                         self.scale)
    self.pixbuf = self.pixbufs.get('mouse')
    self.resize(self.pixbuf.get_width(), self.pixbuf.get_height())

    # a pixmap widget to contain the pixmap
    self.image = gtk.Image()
    bitmap, self.mask = self.pixbuf.render_pixmap_and_mask()
    self.image.set_from_pixmap(bitmap, self.mask)
    self.image.show()
    self.add(self.image)

  def _on_size_allocate(self, win, unused_allocation):
    """Called when first allocated."""
    # Set the window shape
    win.shape_combine_mask(self.mask, 0, 0)
    win.set_property('skip-taskbar-hint', True)
    if not win.is_composited():
      print 'Unable to fade the window'
    else:
      win.set_opacity(0.5)

  def center_on_cursor(self, x=None, y=None):
    if x is None or y is None:
      root = gtk.gdk.screen_get_default().get_root_window()
      x, y, _ = root.get_pointer()
    w, h = self.get_size()
    new_x, new_y = x - w/2, y - h/2
    pos = self.get_position()
    if pos[0] != new_x or pos[1] != new_y:
      self.move(new_x, new_y)
      self.show()

  def show(self):
    self.is_shown = True
    self.present()

  def hide(self):
    self.is_shown = False
    gtk.Window.hide(self)

  def fade_away(self):
    """Make the window fade in a little bit."""
    self.present()
    gobject.timeout_add(200, self.hide)
