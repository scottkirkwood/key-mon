#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""


"""

__author__ = 'scott@forusers.com (scottkirkwood))'

import sys
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import logging

import evdev
import two_state_image
import lazy_pixbuf_creator
try:
  import dbus
except:
  print "Unable to import dbus interface, quitting"
  sys.exit(-1)

def FixSvgKeyClosure(from_str, to_str):
  """Create a closure to modify the key."""

  def FixSvgKey(bytes):
    """Given an SVG file (as bytes) return the SVG fixed."""
    return bytes.replace(from_str, to_str)
  return FixSvgKey

NAME_FNAMES = {
  'MOUSE': ['svg/mouse.svg',],
  'BTN_LEFT': ['svg/mouse.svg', 'svg/left-mouse.svg'],
  'BTN_RIGHT': ['svg/mouse.svg', 'svg/right-mouse.svg'],
  'BTN_MIDDLE': ['svg/mouse.svg', 'svg/middle-mouse.svg'],
  'SCROLL_UP': ['svg/mouse.svg', 'svg/scroll-up-mouse.svg'],
  'SCROLL_DN': ['svg/mouse.svg', 'svg/scroll-dn-mouse.svg'],
  'SHIFT': ['svg/shift.svg'],
  'SHIFT_EMPTY': ['svg/shift.svg', 'svg/whiteout-72.svg'],
  'CTRL': ['svg/ctrl.svg'],
  'CTRL_EMPTY': ['svg/ctrl.svg', 'svg/whiteout-58.svg'],
  'META': ['svg/meta.svg'],
  'META_EMPTY': ['svg/meta.svg', 'svg/whiteout-58.svg'],
  'ALT': ['svg/alt.svg'],
  'ALT_EMPTY': ['svg/alt.svg', 'svg/whiteout-58.svg'],
  'KEY_EMPTY': ['svg/key-empty.svg'],
  'KEY_SPACE': ['svg/spacebar.svg'],
  'KEY_TAB': ['svg/tab.svg'],
}


class KeyMon:
  def __init__(self):
    bus = dbus.SystemBus()

    hal_obj = bus.get_object ("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
    hal = dbus.Interface(hal_obj, "org.freedesktop.Hal.Manager")

    self.GetKeyboardDevices(bus, hal)
    self.GetMouseDevices(bus, hal) 
    self.pixbufs = lazy_pixbuf_creator.LazyPixbufCreator(NAME_FNAMES)
    self.CreateWindow()

  def CreateWindow(self):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

    self.window.set_title('Keyboard Status Monitor')
    self.window.set_default_size(328, 48)
    self.window.set_decorated(False) 
    self.window.set_keep_above(True) 
    width, height = 328, 48
    
    self.event_box = gtk.EventBox()
    self.window.add(self.event_box)
    self.event_box.show()

    self.hbox = gtk.HBox(False, 0)
    self.event_box.add(self.hbox)

    self.mouse_image = two_state_image.TwoStateImage(self.pixbufs, 'MOUSE')
    self.hbox.pack_start(self.mouse_image, False, True, 0)
    self.shift_image = two_state_image.TwoStateImage(self.pixbufs, 'SHIFT_EMPTY')
    self.hbox.pack_start(self.shift_image, False, True, 0)
    self.ctrl_image = two_state_image.TwoStateImage(self.pixbufs, 'CTRL_EMPTY')
    self.hbox.pack_start(self.ctrl_image, False, True, 0)
    self.meta_image = two_state_image.TwoStateImage(self.pixbufs, 'META_EMPTY')
    self.hbox.pack_start(self.meta_image, False, True, 0)
    self.alt_image = two_state_image.TwoStateImage(self.pixbufs, 'ALT_EMPTY')
    self.hbox.pack_start(self.alt_image, False, True, 0)
    self.key_image = two_state_image.TwoStateImage(self.pixbufs, 'KEY_EMPTY')
    self.hbox.pack_start(self.key_image, False, True, 0)

    self.buttons = [self.mouse_image, self.shift_image, self.ctrl_image,
        self.meta_image, self.alt_image, self.key_image]

    self.hbox.show()
    self.AddEvents()

    self.window.show()

  def AddEvents(self):
    self.window.connect('destroy', self.Destroy)
    self.event_box.connect('button_release_event', self.RightClickHandler)

    try:
      self.devices = evdev.DeviceGroup(self.keyboard_filenames +
                                       self.mouse_filenames)
    except OSError, e:
      print 'You may need to run this as %r' % 'sudo %s' % sys.argv[0]
      sys.exit(-1)
    gobject.idle_add(self.OnIdle)

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
      print event
      self.HandleMouseScroll(event.value)

  def HandleKey(self, code):
    print 'Key %s pressed' % code
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
      self.meta_image.SwitchTo('META')
      return
    if len(code) == 5 and code.startswith('KEY_'):
      letter = code[-1]
      letter_name = 'KEY_%s' % letter
      if letter not in NAME_FNAMES:
        NAME_FNAMES[letter_name] = ['svg/key-template.svg', 
            FixSvgKeyClosure('&amp;', letter)]
      self.key_image.SwitchTo(letter_name)
      return
    if code in NAME_FNAMES:
      self.key_image.SwitchTo(code)

  def HandleMouseButton(self, code):
    self.mouse_image.SwitchTo(code)
    return True

  def HandleMouseScroll(self, dir):
    print 'Mouse scroll %d' % dir
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
    if current:
      print 'toggle chrome off'
    else:
      print 'toggle chrome on'
    self.window.set_decorated(not current) 

  def ToggleMetaKey(self, current):
    if current:
      self.meta_image.hide()
      self.set_show_no_all(True)
    else:
      self.set_show_no_all(False)
      self.meta_image.show()

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
  keymon = KeyMon()
  gtk.main()
