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
import logging

import evdev
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
  'SHIFT': ['svg/shift.svg'],
  'CTRL': ['svg/ctrl.svg'],
  'KEY_UP_EMPTY': ['svg/key-template.svg',],
  'KEY_DOWN_LETTER': ['svg/key-template_dark.svg', FixSvgKey]
}


class LazyImageCreator():
  """Class to create SVG images on the fly."""
  def __init__(self, name_fnames):
    """Initialize with empty.
    
    Args:
      name_fnames: List of names to filename list.
    """
    self.images = {}
    self.name_fnames = name_fnames

  def Get(self, name):
    if name not in self.images:
      name = self.CreateImage(name)
    self.images[name].show()
    return self.images[name]

  def CreateImage(self, name):
    """Creates the image.
    Args:
      name: name of the image we are to create.
    Returns:
      The name given or EMPTY if error.
    """
    if name not in self.name_fnames:
      logging.error('Don\'t understand the name %r' % name)
      return 'KEY_UP_EMPTY'
    ops = self.name_fnames[name]
    if len(ops) == 1:
      self.images[name] = gtk.Image()
      self.images[name].set_from_file(ops[0])
    else:
      print ops

    return name
    
    
class KeyMon:
  def __init__(self):
    bus = dbus.SystemBus()

    hal_obj = bus.get_object ("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
    hal = dbus.Interface(hal_obj, "org.freedesktop.Hal.Manager")

    self.GetKeyboard(bus, hal)
    self.GetMouse(bus, hal) 
    self.images = LazyImageCreator(NAME_FNAMES)
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

    self.hbox.pack_start(self.images.Get('MOUSE'), False, False, 0)
    self.hbox.pack_start(self.images.Get('SHIFT'), False, False, 0)
    self.hbox.pack_start(self.images.Get('CTRL'), False, False, 0)
    
    self.hbox.show()
    self.AddEvents()
    
    self.window.show()
  
  def AddEvents(self):
    self.window.connect('destroy', self.Destroy)
    self.event_box.connect('button_release_event', self.RightClickHandler)

  def Destroy(self, widget, data=None):
    gtk.main_quit()

  def RightClickHandler(self, widget, event):
    print 'Clicked'
    

  def GetKeyboard(self, bus, hal):
    self.keyboard_devices = hal.FindDeviceByCapability("input.keyboard")
    if not self.keyboard_devices:
      print "No keyboard devices found"
      sys.exit(-1)

    self.keyboard_filenames = []
    for keyboard_device in self.keyboard_devices:
      dev_obj = bus.get_object ("org.freedesktop.Hal", keyboard_device)
      dev = dbus.Interface (dev_obj, "org.freedesktop.Hal.Device")
      self.keyboard_filenames.append(dev.GetProperty("input.device"))

  def GetMouse(self, bus, hal):
    self.mouse_devices = hal.FindDeviceByCapability ("input.mouse")
    if not self.mouse_devices:
      print "No mouse devices found"
      sys.exit(-1)
    self.mouse_filenames = []
    for mouse_device in self.mouse_devices:
      dev_obj = bus.get_object ("org.freedesktop.Hal", mouse_device)
      dev = dbus.Interface (dev_obj, "org.freedesktop.Hal.Device")
      self.mouse_filenames.append(dev.GetProperty("input.device"))
    
  def demo(self):
    """Open the event device named on the command line, use incoming
       events to update a device, and show the state of this device.
       """
    dev = evdev.DeviceGroup(self.keyboard_filenames + self.mouse_filenames)
    while 1:
      event = dev.next_event()
      if event is not None and event.code:
        if event.type == "EV_KEY" and event.value == 1:
          if event.code.startswith("KEY"):
            print event.scanCode, event.code
          elif event.code.startswith("BTN"):
            print event.code
        elif event.type.startswith("EV_REL"):
          print event.code, event.value


if __name__ == "__main__":
  keymon = KeyMon()
  gtk.main()
