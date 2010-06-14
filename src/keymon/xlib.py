#!/usr/bin/python
from Xlib import display
from Xlib import X
from Xlib import XK
from Xlib.ext import record
from Xlib.protocol import rq
import sys
import threading
import collections

class XEvent:
  """An event, mimics edev.py events."""
  def __init__(self, atype, scancode, code, value):
    self._type = atype;
    self._scancode = scancode
    self._code = code
    self._value = value

  def get_type(self):
    return self._type
  type = property(get_type)

  def get_scancode(self):
    return self._scancode
  scancode = property(get_scancode)

  def get_code(self):
    return self._code
  code = property(get_code)

  def get_value(self):
    return self._value
  value = property(get_value)

  def __str__(self):
    return 'type:%s scancode:%s code:%s value:%s' % (self._type, self._scancode, self._code, self._value)
     
class XEvents(threading.Thread):
  _butn_to_code = collections.defaultdict(lambda: 'BTN_DUNNO',
      [(1, 'BTN_LEFT'), (2, 'BTN_MIDDLE'), (3, 'BTN_RIGHT'),
       (4, 'REL_WHEEL'), (5, 'REL_WHEEL')])
  
  def __init__(self):
    threading.Thread.__init__(self)
    self._listening = False
    self.display = display.Display()
    self.local_display = display.Display()
    self.ctx = None
    self.keycode_to_symbol = collections.defaultdict(lambda: 'KEY_DUNNO')
    self._SetupLookup()
    self.events = []  # each of type XEvent

  def run(self):
    self.Start()

  def _SetupLookup(self):
    for name in dir(XK):
      if name[:3] == "XK_":
        code = getattr(XK, name)
        self.keycode_to_symbol[code] = 'KEY_' + name[3:].upper()

  def next_event(self):
    """Returns the next event in queue, or None if none."""
    if self.events:
      return self.events.pop(0)
    return None

  def Start(self):
    if not self.display.has_extension("RECORD"):
      print "RECORD extension not found"
      sys.exit(1)
    self._listening = True
    self.ctx = self.display.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.ButtonRelease),  # why only two, it's a range?
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }])

    self.display.record_enable_context(self.ctx, self._Handler)

    # Don't understand this, how can we free the context yet still use it in Stop?
    self.display.record_free_context(self.ctx)

  def Stop(self):
    if not self._listening:
      return
    self.local_display.record_disable_context(self.ctx)
    self.local_display.flush()
    self.join(0.1)
    self._listening = False

  def Listening(self):
    return self._listening

  def _Handler(self, reply):
    data = reply.data
    while len(data):
      event, data = rq.EventField(None).parse_binary_value(
          data, self.display.display, None, None)
      if event.type == X.ButtonPress:
        self._HandleMouse(event, 1)
      elif event.type == X.ButtonRelease:
        self._HandleMouse(event, 0)
      elif event.type == X.KeyPress:
        self._HandleKey(event, 1)
      elif event.type == X.KeyRelease:
        self._HandleKey(event, 0)
      else:
        print event

  def _HandleMouse(self, event, value):
    """Add a mouse event to events.
    Params:
      event: the event info
      value: 1=down, 0=up
    """ 
    if event.detail in [4, 5]:
      if event.detail == 5:
        value = -1
      else:
        value = 1
      self.events.append(XEvent('EV_REL', 
          0, XEvents._butn_to_code[event.detail], value))
    else:
      self.events.append(XEvent('EV_KEY', 
          0, XEvents._butn_to_code[event.detail], value))

  def _HandleKey(self, event, value):
    """Add key event to events.
    Params:
      event: the event info
      value: 1=down, 0=up
    """
    keysym = self.local_display.keycode_to_keysym(event.detail, 0)
    self.events.append(XEvent('EV_KEY', event.detail - 8, self.keycode_to_symbol[keysym], value))

if __name__ == '__main__':
  e = XEvents()
  e.start()
  try:
    while e.Listening():
      try:
        evt = e.next_event()
      except KeyboardInterrupt:
        print 'User interrupted'
        e.Stop()
      if evt:
        print evt
        if evt.code == 'KEY_ESCAPE':
          e.Stop()
  finally:
    e.Stop()
