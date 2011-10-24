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

"""Library to get X events from Record.

This is designed to read events from X windows for keyboard and mouse
events.
"""

__author__ = 'Scott Kirkwood (scott+keymon@forusers.com)'

from Xlib import display
from Xlib import X
from Xlib import XK
from Xlib.ext import record
from Xlib.protocol import rq
import sys
import time
import threading
import collections

class XEvent(object):
  """An event, mimics edev.py events."""
  def __init__(self, atype, scancode, code, value):
    self._type = atype
    self._scancode = scancode
    self._code = code
    self._value = value

  def get_type(self):
    """Get the type of event."""
    return self._type
  type = property(get_type)

  def get_scancode(self):
    """Get the scancode if any."""
    return self._scancode
  scancode = property(get_scancode)

  def get_code(self):
    """Get the code string."""
    return self._code
  code = property(get_code)

  def get_value(self):
    """Get the value 0 for up, 1 for down, etc."""
    return self._value
  value = property(get_value)

  def __str__(self):
    return 'type:%s scancode:%s code:%s value:%s' % (self._type, 
        self._scancode, self._code, self._value)

class XEvents(threading.Thread):
  """A thread to queue up X window events from RECORD extension."""

  _butn_to_code = collections.defaultdict(lambda: 'BTN_DUNNO',
      [(1, 'BTN_LEFT'), (2, 'BTN_MIDDLE'), (3, 'BTN_RIGHT'),
       (4, 'REL_WHEEL'), (5, 'REL_WHEEL'), (6, 'REL_LEFT'), (7, 'REL_RIGHT')])

  def __init__(self):
    threading.Thread.__init__(self)
    self.setDaemon(True)
    self.setName('Xlib-thread')
    self._listening = False
    self.record_display = display.Display()
    self.local_display = display.Display()
    self.ctx = None
    self.keycode_to_symbol = collections.defaultdict(lambda: 'KEY_DUNNO')
    self._setup_lookup()
    self.events = []  # each of type XEvent

  def run(self):
    """Standard run method for threading."""
    self.start_listening()

  def _setup_lookup(self):
    """Setup the key lookups."""
    for name in dir(XK):
      if name[:3] == "XK_":
        code = getattr(XK, name)
        self.keycode_to_symbol[code] = 'KEY_' + str(unicode(name[3:]).upper())
    self.keycode_to_symbol[65027] = 'KEY_ISO_LEVEL3_SHIFT'
    self.keycode_to_symbol[269025062] = 'KEY_BACK'
    self.keycode_to_symbol[269025063] = 'KEY_FORWARD'
    self.keycode_to_symbol[16777215] = 'KEY_CAPS_LOCK'
    self.keycode_to_symbol[269025067] = 'KEY_WAKEUP'
    # Multimedia keys
    self.keycode_to_symbol[269025042] = 'KEY_AUDIOMUTE'
    self.keycode_to_symbol[269025041] = 'KEY_AUDIOLOWERVOLUME'
    self.keycode_to_symbol[269025043] = 'KEY_AUDIORAISEVOLUME'
    self.keycode_to_symbol[269025047] = 'KEY_AUDIONEXT'
    self.keycode_to_symbol[269025044] = 'KEY_AUDIOPLAY'
    self.keycode_to_symbol[269025046] = 'KEY_AUDIOPREV'
    self.keycode_to_symbol[269025045] = 'KEY_AUDIOSTOP'
    # Turkish / F layout
    self.keycode_to_symbol[699] = 'KEY_GBREVE'   # scancode = 26 / 18
    self.keycode_to_symbol[697] = 'KEY_IDOTLESS' # scancode = 23 / 19
    self.keycode_to_symbol[442] = 'KEY_SCEDILLA' # scancode = 39 / 40


  def next_event(self):
    """Returns the next event in queue, or None if none."""
    if self.events:
      return self.events.pop(0)
    return None

  def start_listening(self):
    """Start listening to RECORD extension and queuing events."""
    if not self.record_display.has_extension("RECORD"):
      print "RECORD extension not found"
      sys.exit(1)
    self._listening = True
    self.ctx = self.record_display.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.MotionNotify),  # why only two, it's a range?
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }])

    self.record_display.record_enable_context(self.ctx, self._handler)

    # Don't understand this, how can we free the context yet still use it in Stop?
    self.record_display.record_free_context(self.ctx)
    self.record_display.close()

  def stop_listening(self):
    """Stop listening to events."""
    if not self._listening:
      return
    self.local_display.record_disable_context(self.ctx)
    self.local_display.flush()
    self.local_display.close()
    self._listening = False
    self.join(0.05)

  def listening(self):
    """Are you listening?"""
    return self._listening

  def _handler(self, reply):
    """Handle an event."""
    if reply.category != record.FromServer:
      return
    if reply.client_swapped:
      return
    data = reply.data
    while len(data):
      event, data = rq.EventField(None).parse_binary_value(
          data, self.record_display.display, None, None)
      if event.type == X.ButtonPress:
        self._handle_mouse(event, 1)
      elif event.type == X.ButtonRelease:
        self._handle_mouse(event, 0)
      elif event.type == X.KeyPress:
        self._handle_key(event, 1)
      elif event.type == X.KeyRelease:
        self._handle_key(event, 0)
      elif event.type == X.MotionNotify:
        self._handle_mouse(event, 2)
      else:
        print event

  def _handle_mouse(self, event, value):
    """Add a mouse event to events.
    Params:
      event: the event info
      value: 2=motion, 1=down, 0=up
    """
    if value == 2:
      self.events.append(XEvent('EV_MOV',
          0, 0, (event.root_x, event.root_y)))
    elif event.detail in [4, 5]:
      if event.detail == 5:
        value = -1
      else:
        value = 1
      self.events.append(XEvent('EV_REL',
          0, XEvents._butn_to_code[event.detail], value))
    else:
      self.events.append(XEvent('EV_KEY',
          0, XEvents._butn_to_code[event.detail], value))

  def _handle_key(self, event, value):
    """Add key event to events.
    Params:
      event: the event info
      value: 1=down, 0=up
    """
    keysym = self.local_display.keycode_to_keysym(event.detail, 0)
    if keysym not in self.keycode_to_symbol:
      print 'Missing code for %d = %d' % (event.detail - 8, keysym)
    self.events.append(XEvent('EV_KEY', event.detail - 8, self.keycode_to_symbol[keysym], value))

def _run_test():
  """Run a test or debug session."""
  events = XEvents()
  events.start()
  while not events.listening():
    time.sleep(1)
    print 'Waiting for initializing...'
  print 'Press ESCape to quit'
  try:
    while events.listening():
      try:
        evt = events.next_event()
      except KeyboardInterrupt:
        print 'User interrupted'
        events.stop_listening()
      if evt:
        print evt
        if evt.code == 'KEY_ESCAPE':
          events.stop_listening()
  finally:
    events.stop_listening()


if __name__ == '__main__':
  _run_test()
