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

def FixSvgKey(bytes, from_str, to_str):
  """Given an SVG file (as bytes) return the SVG fixed."""
  return bytes.replace(from_letter, to_str)

NAME_FNAMES = {
  'MOUSE': ['svg/mouse.svg',],
  'BTN_LEFT': ['svg/mouse.svg', 'svg/left-mouse.svg'],
  'BTN_RIGHT': ['svg/mouse.svg', 'svg/right-mouse.svg'],
  'BTN_MIDDLE': ['svg/mouse.svg', 'svg/middle-mouse.svg'],
  'SHIFT': ['svg/shift.svg'],
  'SHIFT_EMPTY': ['svg/shift.svg', 'svg/whiteout-72.svg'],
  'CTRL': ['svg/ctrl.svg'],
  'CTRL_EMPTY': ['svg/ctrl.svg', 'svg/whiteout-58.svg'],
  'ALT': ['svg/alt.svg'],
  'ALT_EMPTY': ['svg/alt.svg', 'svg/whiteout-58.svg'],
  'KEY_UP_EMPTY': ['svg/key-template.svg'],
  'KEY_X': ['svg/key-template_dark.svg', FixSvgKey]
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
    self.alt_image = two_state_image.TwoStateImage(self.pixbufs, 'ALT_EMPTY')
    self.hbox.pack_start(self.alt_image, False, True, 0)
    self.key_image = two_state_image.TwoStateImage(self.pixbufs, 'KEY_UP_EMPTY')
    self.hbox.pack_start(self.key_image, False, True, 0)

    self.buttons = [self.mouse_image, self.shift_image, self.ctrl_image,
        self.alt_image, self.key_image]
    
    self.hbox.show()
    self.AddEvents()
    
    self.window.show()
  
  def AddEvents(self):
    self.window.connect('destroy', self.Destroy)
    self.event_box.connect('button_release_event', self.RightClickHandler)

    self.devices = evdev.DeviceGroup(self.keyboard_filenames + self.mouse_filenames)
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
    elif code.endswith('ALT'):
      self.alt_image.SwitchTo('ALT')
    elif code.endswith('CTRL'):
      self.ctrl_image.SwitchTo('CTRL')

  def HandleMouseButton(self, code):
    self.mouse_image.SwitchTo(code)

  def HandleMouseScroll(self, dir):
    print 'Mouse scroll %d' % dir

  def Destroy(self, widget, data=None):
    gtk.main_quit()

  def RightClickHandler(self, widget, event):
    if event.button != 3:
      return

    menu = gtk.Menu()

    toggle_chrome = gtk.MenuItem('Window _Chrome')
    toggle_chrome.connect_object('activate', self.ToggleChrome, None)
    toggle_chrome.show()
    menu.append(toggle_chrome)

    quit = gtk.MenuItem('_Quit')
    quit.connect_object('activate', self.Destroy, None)
    quit.show()
    menu.append(quit)

    menu.show()
    menu.popup(None, None, None, event.button, event.time)

  def ToggleChrome(self):
    current = self.window.get_decorated()
    self.window.set_decorated(not current) 

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
