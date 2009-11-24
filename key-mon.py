#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Keyboard Status Monitor.
Monitors one or more keyboards and mouses.
Shows their status graphically.
"""

__author__ = 'scott@forusers.com (scottkirkwood))'

import pygtk
pygtk.require('2.0')
import gobject
import gtk
import logging
import os
import sys

import evdev
import two_state_image
import lazy_pixbuf_creator
try:
  import dbus
except:
  print "Unable to import dbus interface, quitting"
  sys.exit(-1)

def FixSvgKeyClosure(fname, from_tos):
  """Create a closure to modify the key.
  Args:
    from_tos: list of from, to pairs for search replace.
  Returns:
    A bound function which returns the file fname with modifications.
  """

  def FixSvgKey():
    """Given an SVG file return the SVG text fixed."""
    f = open(fname)
    bytes = f.read()
    f.close()
    for f, t in from_tos:
      bytes = bytes.replace(f, t)
    return bytes

  return FixSvgKey


NAME_TO_CHAR = {
    'APOSTROPHE': '\'',
    'ASTERISK': '*',
    'BACKSLASH': '\\',
    'BACKSPACE': u'\u21fd',
    'CAPSLOCK': 'Caps',
    'COMMA': ',',
    'DELETE': 'Del',
    'DOT': '.',
    'END': 'End',
    'ENTER': u'\u23CE',
    'EQUAL': '=',
    'ESC': 'Esc',
    'GRAVE': '`',
    'HOME': 'Home',
    'INSERT': 'Ins',
    'LEFTBRACE': '[',
    'LEFTPAREN': '(',
    'MINUS': '-',
    'PAGEDOWN': 'PgDn',
    'PAGEUP': 'PgUp',
    'PLUS': '+',
    'RIGHTBRACE': ']',
    'RIGHTPAREN': ')',
    'SEMICOLON': ';',
    'SLASH': '/',
}

def NameToChar(name):
  if name in NAME_TO_CHAR:
    return NAME_TO_CHAR[name]
  return name

class KeyMon:
  def __init__(self, scale):
    bus = dbus.SystemBus()
    self.scale = scale
    if scale < 1.0:
      self.svg_size = ''
    else:
      self.svg_size = '-small'
    hal_obj = bus.get_object ("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
    hal = dbus.Interface(hal_obj, "org.freedesktop.Hal.Manager")

    self.enabled = {
        'MOUSE': True,
        'META': False,
    }

    self.GetKeyboardDevices(bus, hal)
    self.GetMouseDevices(bus, hal)
    self.name_fnames = self.CreateNamesToFnames()
    self.pixbufs = lazy_pixbuf_creator.LazyPixbufCreator(self.name_fnames, self.scale)
    self.CreateWindow()

  def CreateNamesToFnames(self):
    return {
      'MOUSE': [self.SvgFname('mouse'),],
      'BTN_LEFT': [self.SvgFname('mouse'), self.SvgFname('left-mouse')],
      'BTN_RIGHT': [self.SvgFname('mouse'), self.SvgFname('right-mouse')],
      'BTN_MIDDLE': [self.SvgFname('mouse'), self.SvgFname('middle-mouse')],
      'SCROLL_UP': [self.SvgFname('mouse'), self.SvgFname('scroll-up-mouse')],
      'SCROLL_DN': [self.SvgFname('mouse'), self.SvgFname('scroll-dn-mouse')],

      'SHIFT': [self.SvgFname('shift')],
      'SHIFT_EMPTY': [self.SvgFname('shift'), self.SvgFname('whiteout-72')],
      'CTRL': [
          FixSvgKeyClosure(self.SvgFname('alt'), [('Alt', 'Ctrl')])],
      'CTRL_EMPTY': [
          FixSvgKeyClosure(self.SvgFname('alt'), [('Alt', 'Ctrl')]), self.SvgFname('whiteout-58')],
      'META': [
          FixSvgKeyClosure(self.SvgFname('alt'), [('Alt', 'Meta')])],
      'META_EMPTY': [
          FixSvgKeyClosure(self.SvgFname('alt'), [('Alt', 'Meta')]), self.SvgFname('whiteout-58')],
      'ALT': [self.SvgFname('alt')],
      'ALT_EMPTY': [self.SvgFname('alt'), self.SvgFname('whiteout-58')],
      'KEY_EMPTY': [
          FixSvgKeyClosure(self.SvgFname('key-template-dark'), [('&amp;', '')]), 
          self.SvgFname('whiteout-48')],
      'KEY_SPACE': [
          FixSvgKeyClosure(self.SvgFname('two-line-wide'), [('TOP', 'Space'), ('BOTTOM', '')])],
      'KEY_TAB': [
          FixSvgKeyClosure(self.SvgFname('two-line-wide'), [('TOP', 'Tab'), ('BOTTOM', u'\u21B9')])],
      'KEY_LEFT': [
          FixSvgKeyClosure(self.SvgFname('key-template-dark'), [('&amp;', u'\u2190')])],
      'KEY_UP': [
          FixSvgKeyClosure(self.SvgFname('key-template-dark'), [('&amp;', u'\u2191')])],
      'KEY_RIGHT': [
          FixSvgKeyClosure(self.SvgFname('key-template-dark'), [('&amp;', u'\u2192')])],
      'KEY_DOWN': [
          FixSvgKeyClosure(self.SvgFname('key-template-dark'), [('&amp;', u'\u2193')])],
      'KEY_BACKSPACE': [
          FixSvgKeyClosure(self.SvgFname('two-line-wide'), [('TOP', 'Back'), ('BOTTOM', u'\u21fd')])],
      'KEY_ENTER': [
          FixSvgKeyClosure(self.SvgFname('two-line-wide'), [('TOP', 'Enter'), ('BOTTOM', u'\u23CE')])],
      'KEY_PAGEUP': [
          FixSvgKeyClosure(self.SvgFname('alt'), [('Alt', 'PgUp')])],
      'KEY_PAGEDOWN': [
          FixSvgKeyClosure(self.SvgFname('alt'), [('Alt', 'PgDn')])],
    }

  def CreateWindow(self):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

    self.window.set_title('Keyboard Status Monitor')
    width, height = 308 * self.scale, 48 * self.scale
    self.window.set_default_size(int(width), int(height))
    self.window.set_decorated(False)
    self.window.set_keep_above(True)

    self.event_box = gtk.EventBox()
    self.window.add(self.event_box)
    self.event_box.show()

    self.hbox = gtk.HBox(False, 0)
    self.event_box.add(self.hbox)

    self.mouse_image = two_state_image.TwoStateImage(self.pixbufs, 'MOUSE')
    self.hbox.pack_start(self.mouse_image, False, False, 0)
    if not self.enabled['MOUSE']:
      self.mouse_image.hide()
    self.shift_image = two_state_image.TwoStateImage(self.pixbufs, 'SHIFT_EMPTY')
    self.hbox.pack_start(self.shift_image, False, False, 0)
    self.ctrl_image = two_state_image.TwoStateImage(self.pixbufs, 'CTRL_EMPTY')
    self.hbox.pack_start(self.ctrl_image, False, False, 0)
    self.meta_image = two_state_image.TwoStateImage(self.pixbufs, 'META_EMPTY',
        self.enabled['META'])
    if not self.enabled['META']:
      self.meta_image.hide()
    self.hbox.pack_start(self.meta_image, False, False, 0)
    self.alt_image = two_state_image.TwoStateImage(self.pixbufs, 'ALT_EMPTY')
    self.hbox.pack_start(self.alt_image, False, False, 0)
    self.key_image = two_state_image.TwoStateImage(self.pixbufs, 'KEY_EMPTY')
    self.hbox.pack_start(self.key_image, True, True, 0)

    self.buttons = [self.mouse_image, self.shift_image, self.ctrl_image,
        self.meta_image, self.alt_image, self.key_image]

    self.hbox.show()
    self.AddEvents()

    self.window.show()

  def SvgFname(self, fname):
    fullname = 'svg/%s%s.svg' % (fname, self.svg_size)
    if self.svg_size and not os.path.exists(fullname):
      # Small not found, defaulting to large size
      fullname = 'svg/%s.svg' % fname
    return fullname

  def AddEvents(self):
    self.window.connect('destroy', self.Destroy)
    self.window.connect('button-press-event', self.ButtonPressed)
    self.event_box.connect('button_release_event', self.RightClickHandler)

    try:
      self.devices = evdev.DeviceGroup(self.keyboard_filenames +
                                       self.mouse_filenames)
    except OSError, e:
      logging.exception(e)
      print
      print 'You may need to run this as %r' % 'sudo %s' % sys.argv[0]
      sys.exit(-1)
    gobject.idle_add(self.OnIdle)

  def ButtonPressed(self, widget, evt):
    if evt.button != 1:
      return True
    widget.begin_move_drag(evt.button, int(evt.x_root), int(evt.y_root), evt.time)
    return True

  def OnIdle(self):
    event = self.devices.next_event()
    self.HandleEvent(event)
    return True  # continue calling

  def HandleEvent(self, event):
    if not event:
      for button in self.buttons:
        button.EmptyEvent()
      return
    if event.type == "EV_KEY" and event.value == 1:
      if event.code.startswith("KEY"):
        self.HandleKey(event.code)
      elif event.code.startswith("BTN"):
        self.HandleMouseButton(event.code)
    elif event.type.startswith("EV_REL") and event.code == 'REL_WHEEL':
      self.HandleMouseScroll(event.value)

  def HandleKey(self, code):
    #print 'Key %s pressed' % code
    if code in self.name_fnames:
      self.key_image.SwitchTo(code)
      return
    if code.endswith('SHIFT'):
      self.shift_image.SwitchTo('SHIFT')
      return
    if code.endswith('ALT'):
      self.alt_image.SwitchTo('ALT')
      return
    if code.endswith('CTRL'):
      self.ctrl_image.SwitchTo('CTRL')
      return
    if code.endswith('META'):
      if self.enabled['META']:
        self.meta_image.SwitchTo('META')
      return
    if code.startswith('KEY_KP'):
      letter = NameToChar(code[6:])
      if code not in self.name_fnames:
        self.name_fnames[code] = [
            FixSvgKeyClosure(self.SvgFname('numpad-template'), [('&amp;', letter)])]
      self.key_image.SwitchTo(code)
      return
    if code.startswith('KEY_'):
      letter = NameToChar(code[4:])
      if code not in self.name_fnames:
        self.name_fnames[code] = [
            FixSvgKeyClosure(self.SvgFname('key-template-dark'), [('&amp;', letter)])]
      self.key_image.SwitchTo(code)
      return

  def HandleMouseButton(self, code):
    if self.enabled['MOUSE']:
      self.mouse_image.SwitchTo(code)
    return True

  def HandleMouseScroll(self, dir):
    if dir > 0:
      self.mouse_image.SwitchTo('SCROLL_UP')
    elif dir < 0:
      self.mouse_image.SwitchTo('SCROLL_DN')
    return True

  def Destroy(self, widget, data=None):
    gtk.main_quit()

  def RightClickHandler(self, widget, event):
    if event.button != 3:
      return

    menu = self.CreateContextMenu()

    menu.show()
    menu.popup(None, None, None, event.button, event.time)

  def CreateContextMenu(self):
    menu = gtk.Menu()

    toggle_chrome = gtk.CheckMenuItem('Window _Chrome')
    toggle_chrome.set_active(self.window.get_decorated())
    toggle_chrome.connect_object('activate', self.ToggleChrome,
       self.window.get_decorated())
    toggle_chrome.show()
    menu.append(toggle_chrome)

    toggle_mouse = gtk.CheckMenuItem('Mouse')
    visible = self.mouse_image.flags() & gtk.VISIBLE
    toggle_mouse.set_active(visible)
    toggle_mouse.connect_object('activate', self.ToggleMouse,
        visible)
    toggle_mouse.show()
    menu.append(toggle_mouse)

    toggle_metakey = gtk.CheckMenuItem('Meta Key')
    visible = self.meta_image.flags() & gtk.VISIBLE
    toggle_metakey.set_active(visible)
    toggle_metakey.connect_object('activate', self.ToggleMetaKey,
        visible)
    toggle_metakey.show()
    menu.append(toggle_metakey)

    quit = gtk.MenuItem('_Quit')
    quit.connect_object('activate', self.Destroy, None)
    quit.show()

    menu.append(quit)
    return menu

  def ToggleChrome(self, current):
    self.window.set_decorated(not current)

  def ToggleMetaKey(self, current):
    self._ToggleAKey(self.meta_image, 'META', current)

  def ToggleMouse(self, current):
    self._ToggleAKey(self.mouse_image, 'MOUSE', current)

  def _ToggleAKey(self, image, name, current):
    if current:
      image.showit = False
      self.enabled[name] = False
      image.hide()
    else:
      image.showit = True
      self.enabled[name] = True
      image.SwitchToDefault()

  def GetKeyboardDevices(self, bus, hal):
    self.keyboard_devices = hal.FindDeviceByCapability("input.keyboard")
    if not self.keyboard_devices:
      print "No keyboard devices found"
      sys.exit(-1)

    self.keyboard_filenames = []
    for keyboard_device in self.keyboard_devices:
      dev_obj = bus.get_object ("org.freedesktop.Hal", keyboard_device)
      dev = dbus.Interface (dev_obj, "org.freedesktop.Hal.Device")
      self.keyboard_filenames.append(dev.GetProperty("input.device"))

  def GetMouseDevices(self, bus, hal):
    self.mouse_devices = hal.FindDeviceByCapability ("input.mouse")
    if not self.mouse_devices:
      print "No mouse devices found"
      sys.exit(-1)
    self.mouse_filenames = []
    for mouse_device in self.mouse_devices:
      dev_obj = bus.get_object ("org.freedesktop.Hal", mouse_device)
      dev = dbus.Interface (dev_obj, "org.freedesktop.Hal.Device")
      self.mouse_filenames.append(dev.GetProperty("input.device"))


if __name__ == "__main__":
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('-s', '--smaller', dest='smaller', default=False, action='store_true',
                    help='Make the dialog 25% smaller than normal.')
  parser.add_option('-l', '--larger', dest='larger', default=False, action='store_true',
                    help='Make the dialog 25% larger than normal.')
  parser.add_option('--scale', dest='scale', default=1.0, type='float',
                    help='Scale the dialog. ex. 2.0 is 2 times larger, 0.5 is half the size.')
  scale = 1.0
  (options, args) = parser.parse_args()
  if options.smaller:
    scale = 0.75
  elif options.larger:
    scale = 1.25
  elif options.scale:
    scale = options.scale
  keymon = KeyMon(scale)
  gtk.main()
