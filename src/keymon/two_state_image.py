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

"""Image that defaults back to a default state after a while.

You can switch the image to something else but it defaults back to the default
image (the first image) after calling EmptyEvent() a few times
"""

__author__ = 'scott@forusers.com (Scott Kirkwood))'

import pygtk
pygtk.require('2.0')
import gtk
import time

DEFAULT_TIMEOUT_SECS = 0.5

class TwoStateImage(gtk.Image):
  """Image has a default image (say a blank image) which it goes back to.
  It can also pass the information down to another image."""
  def __init__(self, pixbufs, normal, show=True, defer_to=None):
    gtk.Image.__init__(self)
    self.pixbufs = pixbufs
    self.normal = normal
    self.count_down = None
    self.showit = show
    self.current = ''
    self.defer_to = defer_to
    self.timeout_secs = DEFAULT_TIMEOUT_SECS
    self.switch_to(self.normal)
    self._really_pressed = False

  def reset_image(self, showit=True):
    """Image from pixbufs has changed, reset."""
    self.showit = showit
    self._switch_to(self.normal)
    self.showit = True

  def is_pressed(self):
    return self.current != self.normal

  @property
  def really_pressed(self):
    "Get the pressing state if a key is physically pressed."
    return self._really_pressed

  @really_pressed.setter
  def really_pressed(self, value):
    """Set if a key is physically pressed.

    This is different than is_pressed(), which is the pressing state of
    indicator, not reflect the real key pressing state. Should be set when key
    event comes in.
    """
    self._really_pressed = value

  def reset_time_if_pressed(self):
    """Start the countdown now."""
    if self.is_pressed():
      self.count_down = time.time()

  def switch_to(self, name):
    """Switch to image with this name."""
    if self.current != self.normal and self.defer_to:
      self._defer_to(self.current)
      # Make sure defer_to image will only start counting timeout after self
      # image has timed out.
      if self.count_down:
        self.defer_to.count_down = self.count_down + self.timeout_secs
      else:
        self.defer_to.count_down += self.timeout_secs
    self._switch_to(name)

  def _switch_to(self, name):
    """Internal, switch to image with this name even if same."""
    self.set_from_pixbuf(self.pixbufs.get(name))
    self.current = name
    self.count_down = None
    if self.showit:
      self.show()

  def switch_to_default(self):
    """Switch to the default image."""
    self.count_down = time.time()

  def empty_event(self):
    """Sort of a idle event.
    
    Returns True if image has been changed.
    """
    if self.count_down is None:
      return
    delta = time.time() - self.count_down
    if delta > self.timeout_secs:
      if self.normal.replace('_EMPTY', '') in ('SHIFT', 'ALT', 'CTRL', 'META') and \
          self.really_pressed:
        return
      self.count_down = None
      self._switch_to(self.normal)
      return True

  def _defer_to(self, old_name):
    """If possible the button is passed on."""
    if not self.defer_to:
      return
    self.defer_to.switch_to(old_name)
    self.defer_to.switch_to_default()
