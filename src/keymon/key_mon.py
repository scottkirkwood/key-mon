#!/usr/bin/python
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Keyboard Status Monitor.
Monitors one or more keyboards and mouses.
Shows their status graphically.
"""

__author__ = 'Scott Kirkwood (scott+keymon@forusers.com)'
__version__ = '1.0'

import logging
import pygtk
pygtk.require('2.0')
import gettext
import gobject
import gtk
import os
import sys
import xlib

import config
import lazy_pixbuf_creator
import mod_mapper
import settings
import shaped_window
import two_state_image

from ConfigParser import SafeConfigParser

gettext.install('key_mon', 'locale')

def FixSvgKeyClosure(fname, from_tos):
  """Create a closure to modify the key.
  Args:
    from_tos: list of from, to pairs for search replace.
  Returns:
    A bound function which returns the file fname with modifications.
  """

  def FixSvgKey():
    """Given an SVG file return the SVG text fixed."""
    logging.debug('Read file %r' % fname)
    f = open(fname)
    fbytes = f.read()
    f.close()
    for f, t in from_tos:
      fbytes = fbytes.replace(f, t)
    return fbytes

  return FixSvgKey


class KeyMon:
  """Main KeyMon window class."""

  def __init__(self, options):
    """Create the Key Mon window.
    Options dict:
      scale: float 1.0 is default which means normal size.
      meta: boolean show the meta (windows key)
      kbd_file: string Use the kbd file given.
      emulate_middle: Emulate the middle mouse button.
      theme: Name of the theme to use to draw keys
    """
    settings.SettingsDialog.Register()
    self.options = options
    self.pathname = os.path.dirname(__file__)
    self.scale = config.get("ui", "scale", float)
    if self.scale < 1.0:
      self.svg_size = '-small'
    else:
      self.svg_size = ''
    self.enabled = {
        'MOUSE': config.get("buttons", "mouse", bool),
        'SHIFT': config.get("buttons", "shift", bool),
        'CTRL': config.get("buttons", "ctrl", bool),
        'META': config.get("buttons", "meta", bool),
        'ALT': config.get("buttons", "alt", bool),
    }
    self.emulate_middle = config.get("devices", "emulate_middle", bool)
    self.modmap = mod_mapper.SafelyReadModMap(config.get("devices", "map"))
    self.swap_buttons = config.get("devices", "swap_buttons", bool)

    self.name_fnames = self.CreateNamesToFnames()
    self.pixbufs = lazy_pixbuf_creator.LazyPixbufCreator(self.name_fnames,
                                                         self.scale)
    self.devices = xlib.XEvents()
    self.devices.start()

    self.CreateWindow()

  def DoScreenshot(self):
    import time
    import evdev
    for key in self.options.screenshot.split(','):
      try:
        scancode = evdev.Event.codeMaps['EV_KEY'].toNumber(key)
        event = xlib.XEvent('EV_KEY', scancode=scancode, code=key, value=1)
        self.HandleEvent(event)
        while gtk.events_pending():
          gtk.main_iteration(False)
        time.sleep(0.1)
      except Exception, e:
        print e
    while gtk.events_pending():
      gtk.main_iteration(False)
    time.sleep(0.1)
    win = self.window
    x, y = win.get_position()
    w, h = win.get_size()
    screenshot = gtk.gdk.Pixbuf.get_from_drawable(
        gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h),
        gtk.gdk.get_default_root_window(),
        gtk.gdk.colormap_get_system(),
        x, y, 0, 0, w, h)
    fname = 'screenshot.png'
    screenshot.save(fname, 'png')
    print 'Saved screenshot %r' % fname
    self.Destroy(None)

  def CreateNamesToFnames(self):
    ftn = {
      'MOUSE': [self.SvgFname('mouse'),],
      'BTN_MIDDLE': [self.SvgFname('mouse'), self.SvgFname('middle-mouse')],
      'SCROLL_UP': [self.SvgFname('mouse'), self.SvgFname('scroll-up-mouse')],
      'SCROLL_DOWN': [self.SvgFname('mouse'), self.SvgFname('scroll-dn-mouse')],

      'SHIFT': [self.SvgFname('shift')],
      'SHIFT_EMPTY': [self.SvgFname('shift'), self.SvgFname('whiteout-72')],
      'CTRL': [self.SvgFname('ctrl')],
      'CTRL_EMPTY': [self.SvgFname('ctrl'), self.SvgFname('whiteout-58')],
      'META': [self.SvgFname('meta'), self.SvgFname('meta')],
      'META_EMPTY': [self.SvgFname('meta'), self.SvgFname('whiteout-58')],
      'ALT': [self.SvgFname('alt')],
      'ALT_EMPTY': [self.SvgFname('alt'), self.SvgFname('whiteout-58')],
      'KEY_EMPTY': [
          FixSvgKeyClosure(self.SvgFname('one-char-template'), [('&amp;', '')]),
              self.SvgFname('whiteout-48')],
      'BTN_LEFTRIGHT': [
          self.SvgFname('mouse'), self.SvgFname('left-mouse'), self.SvgFname('right-mouse')],
    }
    if self.swap_buttons:
      ftn.update({
        'BTN_RIGHT': [self.SvgFname('mouse'), self.SvgFname('left-mouse')],
        'BTN_LEFT': [self.SvgFname('mouse'), self.SvgFname('right-mouse')],
      })
    else:
      ftn.update({
        'BTN_LEFT': [self.SvgFname('mouse'), self.SvgFname('left-mouse')],
        'BTN_RIGHT': [self.SvgFname('mouse'), self.SvgFname('right-mouse')],
      })

    if self.scale >= 1.0:
      ftn.update({
        'KEY_SPACE': [
            FixSvgKeyClosure(self.SvgFname('two-line-wide'),
            [('TOP', 'Space'), ('BOTTOM', '')])],
        'KEY_TAB': [
            FixSvgKeyClosure(self.SvgFname('two-line-wide'),
            [('TOP', 'Tab'), ('BOTTOM', u'\u21B9')])],
        'KEY_BACKSPACE': [
            FixSvgKeyClosure(self.SvgFname('two-line-wide'),
            [('TOP', 'Back'), ('BOTTOM', u'\u21fd')])],
        'KEY_RETURN': [
            FixSvgKeyClosure(self.SvgFname('two-line-wide'),
            [('TOP', 'Enter'), ('BOTTOM', u'\u23CE')])],
        'KEY_CAPS_LOCK': [
            FixSvgKeyClosure(self.SvgFname('two-line-wide'),
            [('TOP', 'Capslock'), ('BOTTOM', '')])],
      })
    else:
      ftn.update({
        'KEY_SPACE': [
            FixSvgKeyClosure(self.SvgFname('one-line-wide'), [('&amp;', 'Space')])],
        'KEY_TAB': [
            FixSvgKeyClosure(self.SvgFname('one-line-wide'), [('&amp;', 'Tab')])],
        'KEY_BACKSPACE': [
            FixSvgKeyClosure(self.SvgFname('one-line-wide'), [('&amp;', 'Back')])],
        'KEY_RETURN': [
            FixSvgKeyClosure(self.SvgFname('one-line-wide'), [('&amp;', 'Enter')])],
        'KEY_CAPS_LOCK': [
            FixSvgKeyClosure(self.SvgFname('one-line-wide'), [('&amp;', 'Capslck')])],
      })
    return ftn

  def CreateWindow(self):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

    self.window.set_title('Keyboard Status Monitor')
    width, height = 30 * self.scale, 48 * self.scale
    self.window.set_default_size(int(width), int(height))
    self.window.set_decorated(config.get("ui", "decorated", bool))

    self.mouse_indicator_win = shaped_window.ShapedWindow(self.SvgFname('mouse-indicator'))

    #self.window.set_opacity(1.0)
    self.window.set_keep_above(True)

    self.event_box = gtk.EventBox()
    self.window.add(self.event_box)
    self.event_box.show()

    self.hbox = gtk.HBox(False, 0)
    self.event_box.add(self.hbox)

    self.mouse_image = two_state_image.TwoStateImage(self.pixbufs, 'MOUSE')
    if not self.enabled['MOUSE']:
      self.mouse_image.hide()
    self.hbox.pack_start(self.mouse_image, False, False, 0)
    if not self.enabled['MOUSE']:
      self.mouse_image.hide()

    self.shift_image = two_state_image.TwoStateImage(
        self.pixbufs, 'SHIFT_EMPTY', self.enabled['SHIFT'])
    if not self.enabled['SHIFT']:
      self.shift_image.hide()
    self.hbox.pack_start(self.shift_image, False, False, 0)

    self.ctrl_image = two_state_image.TwoStateImage(
        self.pixbufs, 'CTRL_EMPTY')
    if not self.enabled['CTRL']:
      self.ctrl_image.hide()
    self.hbox.pack_start(self.ctrl_image, False, False, 0)

    self.meta_image = two_state_image.TwoStateImage(
        self.pixbufs, 'META_EMPTY', self.enabled['META'])
    if not self.enabled['META']:
      self.meta_image.hide()
    self.hbox.pack_start(self.meta_image, False, False, 0)

    self.alt_image = two_state_image.TwoStateImage(
        self.pixbufs, 'ALT_EMPTY', self.enabled['ALT'])
    if not self.enabled['ALT']:
      self.alt_image.hide()
    self.hbox.pack_start(self.alt_image, False, False, 0)

    self.buttons = [self.mouse_image, self.shift_image, self.ctrl_image,
        self.meta_image, self.alt_image]

    prev_key_image = None
    for n in range(self.options.old_keys):
      key_image = two_state_image.TwoStateImage(self.pixbufs, 'KEY_EMPTY')
      key_image.hide()
      key_image.timeout_secs = 0.5
      key_image.defer_to = prev_key_image
      self.hbox.pack_start(key_image, True, True, 0)
      self.buttons.append(key_image)
      prev_key_image = key_image

    # This must be after the loop above.
    self.key_image = two_state_image.TwoStateImage(self.pixbufs, 'KEY_EMPTY')
    self.key_image.timeout_secs = 0.5

    self.buttons.append(self.key_image)
    self.key_image.defer_to = prev_key_image
    self.hbox.pack_start(self.key_image, True, True, 0)

    self.hbox.show()
    self.AddEvents()

    old_x = config.get('position', 'x', int)
    old_y = config.get('position', 'y', int)
    if old_x != -1 and old_y != -1 and old_x and old_y:
      self.window.move(old_x, old_y)
    self.window.show()

  def SvgFname(self, fname):
    fullname = os.path.join(self.pathname, 'themes/%s/%s%s.svg' % (
        config.get("ui", "theme"), fname, self.svg_size))
    if self.svg_size and not os.path.exists(fullname):
      # Small not found, defaulting to large size
      fullname = os.path.join(self.pathname, 'themes/%s/%s.svg' %
                              (config.get("ui", "theme"), fname))
    return fullname

  def AddEvents(self):
    self.window.connect('destroy', self.Destroy)
    self.window.connect('button-press-event', self.ButtonPressed)
    self.window.connect('configure-event', self._WindowMoved)
    self.event_box.connect('button_release_event', self.RightClickHandler)

    accelgroup = gtk.AccelGroup()
    key, modifier = gtk.accelerator_parse('<Control>q')
    accelgroup.connect_group(key, modifier, gtk.ACCEL_VISIBLE, self.Quit)
    self.window.add_accel_group(accelgroup)

    if self.options.screenshot:
      gobject.timeout_add(700, self.DoScreenshot)
      return

    gobject.idle_add(self.OnIdle)

  def ButtonPressed(self, widget, evt):
    if evt.button != 1:
      return True
    widget.begin_move_drag(evt.button, int(evt.x_root), int(evt.y_root), evt.time)
    return True

  def _WindowMoved(self, widget, event):
    x, y = widget.get_position()
    logging.info('Moved window to %d, %d' % (x, y))
    config.set('position', 'x', x)
    config.set('position', 'y', y)

  def OnIdle(self):
    event = self.devices.next_event()
    try:
      self.HandleEvent(event)
    except KeyboardInterrupt:
      print 'Quit from OnIdle()'
      self.Quit()
      return False
    return True  # continue calling

  def HandleEvent(self, event):
    if not event:
      for button in self.buttons:
        button.EmptyEvent()
      return
    if event.type == 'EV_KEY' and event.value in (0, 1):
      if type(event.code) == str:
        if event.code.startswith('KEY'):
          code_num = event.scancode
          self.HandleKey(code_num, event.value)
        elif event.code.startswith('BTN'):
          self.HandleMouseButton(event.code, event.value)
    elif event.type.startswith('EV_REL') and event.code == 'REL_WHEEL':
      self.HandleMouseScroll(event.value, event.value)

  def _HandleEvent(self, image, name, code):
    if code == 1:
      logging.debug('Switch to %s, code %s' % (name, code))
      image.SwitchTo(name)
    else:
      image.SwitchToDefault()


  def HandleKey(self, scan_code, value):
    if scan_code in self.modmap:
      code, medium_name, short_name = self.modmap[scan_code]
    else:
      print 'No mapping for scan_code %d' % scan_code
      return
    if self.scale < 1.0 and short_name:
      medium_name = short_name
    logging.debug('Key %s pressed = %r' % (code, medium_name))
    if code in self.name_fnames:
      self._HandleEvent(self.key_image, code, value)
      return
    if code.startswith('KEY_SHIFT'):
      if self.enabled['SHIFT']:
        self._HandleEvent(self.shift_image, 'SHIFT', value)
      return
    if code.startswith('KEY_ALT') or code == 'KEY_ISO_LEVEL3_SHIFT':
      if self.enabled['ALT']:
        self._HandleEvent(self.alt_image, 'ALT', value)
      return
    if code.startswith('KEY_CONTROL'):
      if self.enabled['CTRL']:
        self._HandleEvent(self.ctrl_image, 'CTRL', value)
      return
    if code.startswith('KEY_SUPER') or code == 'KEY_MULTI_KEY':
      if self.enabled['META']:
        self._HandleEvent(self.meta_image, 'META', value)
      return
    if code.startswith('KEY_KP'):
      letter = medium_name
      if code not in self.name_fnames:
        template = 'one-char-numpad-template'
        self.name_fnames[code] = [
            FixSvgKeyClosure(self.SvgFname(template), [('&amp;', letter)])]
      self._HandleEvent(self.key_image, code, value)
      return
    if code.startswith('KEY_'):
      letter = medium_name
      if code not in self.name_fnames:
        logging.debug('code not in %s' % code)
        if len(letter) == 1:
          template = 'one-char-template'
        else:
          template = 'multi-char-template'
        self.name_fnames[code] = [
            FixSvgKeyClosure(self.SvgFname(template), [('&amp;', letter)])]
      else:
        logging.debug('code in %s' % code)
      self._HandleEvent(self.key_image, code, value)
      return

  def HandleMouseButton(self, code, value):
    if self.enabled['MOUSE']:
      if self.emulate_middle and ((self.mouse_image.current == 'BTN_LEFT' and code == 'BTN_RIGHT') or
          (self.mouse_image.current == 'BTN_RIGHT' and code == 'BTN_LEFT')):
        code = 'BTN_MIDDLE'
      elif value == 1 and ((self.mouse_image.current == 'BTN_LEFT' and code == 'BTN_RIGHT') or
          (self.mouse_image.current == 'BTN_RIGHT' and code == 'BTN_LEFT')):
        code = 'BTN_LEFTRIGHT'
      elif value == 0 and self.mouse_image.current == 'BTN_LEFTRIGHT':
        value = 1  # Pretend it was clicked.
        if code == 'BTN_LEFT':
          code = 'BTN_RIGHT'
        elif code == 'BTN_RIGHT':
          code = 'BTN_LEFT'
      self._HandleEvent(self.mouse_image, code, value)

    root = gtk.gdk.screen_get_default().get_root_window()
    x, y, mods = root.get_pointer()
    w, h = self.mouse_indicator_win.get_size()
    self.mouse_indicator_win.move(x - w/2, y - h/2)
    if value == 0 and config.get('ui', 'visible-click', bool):
      self.mouse_indicator_win.FadeAway()
    return True

  def HandleMouseScroll(self, dir, value):
    if dir > 0:
      self._HandleEvent(self.mouse_image, 'SCROLL_UP', 1)
    elif dir < 0:
      self._HandleEvent(self.mouse_image, 'SCROLL_DOWN', 1)
    self.mouse_image.SwitchToDefault()
    return True

  def Quit(self, *args):
    self.devices.Stop()
    self.Destroy(None)

  def Destroy(self, widget, data=None):
    self.devices.Stop()
    config.cleanup()
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

    settings_click = gtk.MenuItem('_Settings...')
    settings_click.connect_object('activate', self.ShowSettingsDlg, None)
    settings_click.show()
    menu.append(settings_click)

    quit = gtk.MenuItem('_Quit\tCtrl-Q')
    quit.connect_object('activate', self.Destroy, None)
    quit.show()

    menu.append(quit)
    return menu

  def ToggleChrome(self, current):
    self.window.set_decorated(not current)
    config.set('ui', 'decorated', not current)

  def ShowSettingsDlg(self, unused_arg):
    dlg = settings.SettingsDialog(self.window)
    dlg.connect('settings-changed', self.SettingsChanged)
    dlg.show_all()
    dlg.run()
    dlg.destroy()

  def SettingsChanged(self, dlg):
    self._ToggleAKey(self.mouse_image, 'MOUSE',
        config.get('buttons', 'mouse', bool))
    self._ToggleAKey(self.meta_image, 'META',
        config.get('buttons', 'meta', bool))
    self._ToggleAKey(self.shift_image, 'SHIFT',
        config.get('buttons', 'shift', bool))
    self._ToggleAKey(self.ctrl_image, 'CTRL',
        config.get('buttons', 'ctrl', bool))
    self._ToggleAKey(self.alt_image, 'ALT',
        config.get('buttons', 'ALT', bool))
    if config.get('ui', 'visible-click', bool):
      self.mouse_indicator_win.FadeAway()
    self.window.set_decorated(config.get('ui', 'decorated', bool))

  def _ToggleAKey(self, image, name, show):
    if self.enabled[name] == show:
      return
    if show:
      image.showit = True
      self.enabled[name] = True
      image.SwitchToDefault()
    else:
      image.showit = False
      self.enabled[name] = False
      image.hide()

def ShowVersion():
  print 'Keymon version %s.' % __version__
  print 'Written by %s' % __author__

def Main():
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('-s', '--smaller', dest='smaller', default=False, action='store_true',
                    help='Make the dialog 25% smaller than normal.')
  parser.add_option('-l', '--larger', dest='larger', default=False, action='store_true',
                    help='Make the dialog 25% larger than normal.')
  parser.add_option('-m', '--meta', dest='meta', action='store_true',
                    default=config.get('buttons', 'meta', bool),
                    help='Show the meta (windows) key.')
  parser.add_option('--nometa', dest='meta', action='store_false',
                    help='Don\'t show the meta (windows) key.')
  parser.add_option('--mouse', dest='nomouse', action='store_false',
                    default=not config.get('buttons', 'mouse', bool),
                    help='Show the mouse.')
  parser.add_option('--nomouse', dest='nomouse', action='store_true',
                    help='Hide the mouse.')
  parser.add_option('--shift', dest='noshift', action='store_false',
                    default=not config.get('buttons', 'shift', bool),
                    help='Show shift key.')
  parser.add_option('--noshift', dest='noshift', action='store_true',
                    help='Don\'t show the shift key.')
  parser.add_option('--ctrl', dest='noctrl', action='store_false',
                    default=not config.get('buttons', 'ctrl', bool),
                    help='Show the ctrl key.')
  parser.add_option('--noctrl', dest='noctrl', action='store_true',
                    help='Hide the ctrl key.')
  parser.add_option('--alt', dest='noalt', action='store_false',
                    default=not config.get('buttons', 'alt', bool),
                    help='Show the alt key.')
  parser.add_option('--noalt', dest='noalt', action='store_true',
                    help='Hide the alt key.')
  parser.add_option('--scale', dest='scale',
                    default=config.get('ui', 'scale', float),
                    type='float',
                    help='Scale the dialog. ex. 2.0 is 2 times larger, 0.5 is '
                         'half the size. Defaults to %default')
  parser.add_option('--decorated', dest='decorated', action='store_true',
                    default=config.get('ui', 'decorated', bool),
                    help='Show decoration')
  parser.add_option('--notdecorated', dest='decorated', action='store_false',
                    help='No decoration')
  parser.add_option('--visible_click', dest='visible_click', action='store_true',
                    default=config.get('ui', 'visible-click', bool),
                    help='Show where you clicked')
  parser.add_option('--novisible_click', dest='visible_click', action='store_false',
                    help='Turn off the visible button clicks.')
  parser.add_option('--kbdfile', dest='kbd_file',
                    default=config.get('devices', 'map'),
                    help='Use this kbd filename instead running xmodmap.')
  parser.add_option('--swap', dest='swap_buttons', action='store_true',
                    help='Swap the mouse buttons.')
  parser.add_option('--emulate-middle', dest='emulate_middle', action='store_true',
                    help=('When you press the left, and right mouse buttons at the same time, '
                          'it displays as a middle mouse button click. '))
  parser.add_option('-v', '--version', dest='version', action='store_true',
                    help='Show version information and exit.')
  parser.add_option('-t', '--theme', dest='theme',
                    default=config.get('ui', 'theme'),
                    help='The theme to use when drawing status images (ex. "-t apple").')
  parser.add_option('--list-themes', dest='list_themes', action='store_true',
                    help='List available themes')
  parser.add_option('--old-keys', dest='old_keys', type='int',
                    help='How many historical keypresses to show (defaults to %default)',
                    default=config.get('buttons', 'old-keys', int))

  group = optparse.OptionGroup(parser, 'Developer Options',
                    'These options are for developers.')
  group.add_option('-d', '--debug', dest='debug', action='store_true',
                    help='Output debugging information.')
  group.add_option('--screenshot', dest='screenshot',
                    help='Create a "screenshot.png" and exit. '
                    'Pass a comma separated list of keys to simulate (ex. "KEY_A,KEY_LEFTCTRL").')
  parser.add_option_group(group)

  (options, args) = parser.parse_args()

  if options.version:
    ShowVersion()
    sys.exit(-1)
  if options.debug:
    logging.basicConfig(
        level=logging.DEBUG,
        format = '%(filename)s [%(lineno)d]: %(levelname)s %(message)s')
  if options.smaller:
    options.scale = 0.75
  elif options.larger:
    options.scale = 1.25
  if options.list_themes:
    print 'Available themes:'
    for entry in sorted(os.listdir('themes')):
      try:
        parser = SafeConfigParser()
        parser.read(os.path.join('themes', entry, 'config'))
        desc = parser.get('theme', 'description')
        print '%s: %s' % (entry, desc)
      except:
        pass
    raise SystemExit()

  config.set('ui', 'scale', options.scale)
  config.set('ui', 'theme', options.theme)

  if options.nomouse is not None:
    config.set('buttons', 'mouse', not options.nomouse)
  if options.noshift is not None:
    config.set('buttons', 'shift', not options.noshift)
  if options.noctrl is not None:
    config.set('buttons', 'ctrl', not options.noctrl)
  if options.noalt is not None:
    config.set('buttons', 'alt', not options.noalt)
  if options.meta is not None:
    config.set('buttons', 'meta', options.meta)
  config.set('buttons', 'old-keys', options.old_keys)

  config.set('devices', 'map', options.kbd_file)
  config.set('devices', 'emulate_middle', bool(options.emulate_middle))
  config.set('devices', 'swap_buttons', bool(options.swap_buttons))

  keymon = KeyMon(options)
  try:
    gtk.main()
  except KeyboardInterrupt:
    print 'Quit from gtk.main()'
    keymon.Quit()

if __name__ == '__main__':
  Main()
