#!/usr/bin/python
from Xlib import display
from Xlib import X
from Xlib import XK
from Xlib.ext import record
from Xlib.protocol import rq
import sys

class XEvents:
  def __init__(self):
    self.display = display.Display()
    self.local_display = display.Display()
    self.ctx = None
    self.keycode_to_symbol = {}
    self.SetupLookup()

  def SetupLookup(self):
    for name in dir(XK):
      if name[:3] == "XK_":
        code = getattr(XK, name)
        self.keycode_to_symbol[code] = 'KEY_' + name[3:]

  def Start(self):
    if not self.display.has_extension("RECORD"):
      print "RECORD extension not found"
      sys.exit(1)
    self.ctx = self.display.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.ButtonPress),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }])

    self.display.record_enable_context(self.ctx, self.Handler)
    self.display.record_free_context(self.ctx)

  def Stop(self):
    self.local_display.record_disable_context(self.ctx)
    self.local_display.flush()

  def Handler(self, reply):
    data = reply.data
    while len(data):
      event, data = rq.EventField(None).parse_binary_value(
          data, self.display.display, None, None)
      if event.type == X.ButtonPress:
        print 'release', event.detail
      elif event.type == X.ButtonRelease:
        print 'release', event.detail
      elif event.type in (X.KeyPress, X.KeyRelease):
        keysym = self.local_display.keycode_to_keysym(event.detail, 0)
        if keysym in self.keycode_to_symbol:
          print self.keycode_to_symbol[keysym]
        else:
          print 'key press unknown', keysym
        if event.type == X.KeyPress and keysym == XK.XK_Escape:
          self.Stop()
          sys.exit(-1)

if __name__ == '__main__':
  e = XEvents()
  e.Start()
