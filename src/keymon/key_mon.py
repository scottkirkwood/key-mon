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

"""Keyboard Status Monitor.
Monitors one or more keyboards and mouses.
Shows their status graphically.
"""

__author__ = 'Scott Kirkwood (scott+keymon@forusers.com)'
__version__ = '1.2.5'

import logging
import pygtk
pygtk.require('2.0')
import gettext
import gobject
import gtk
import os
import sys
try:
  import xlib
except ImportError:
  print 'Error: Missing xlib, run sudo apt-get install python-xlib'
  sys.exit(-1)

import config
import lazy_pixbuf_creator
import mod_mapper
import settings
import shaped_window
import two_state_image

from ConfigParser import SafeConfigParser

gettext.install('key-mon', 'locale')

def fix_svg_key_closure(fname, from_tos):
  """Create a closure to modify the key.
  Args:
    from_tos: list of from, to pairs for search replace.
  Returns:
    A bound function which returns the file fname with modifications.
  """

  def fix_svg_key():
    """Given an SVG file return the SVG text fixed."""
    logging.debug('Read file %r', fname)
    fin = open(fname)
    fbytes = fin.read()
    fin.close()
    for fin, t in from_tos:
      fbytes = fbytes.replace(fin, t)
    return fbytes

  return fix_svg_key


class KeyMon:
  """main KeyMon window class."""

  def __init__(self, options):
    """Create the Key Mon window.
    Options dict:
      scale: float 1.0 is default which means normal size.
      meta: boolean show the meta (windows key)
      kbd_file: string Use the kbd file given.
      emulate_middle: Emulate the middle mouse button.
      theme: Name of the theme to use to draw keys
    """
    settings.SettingsDialog.register()
    self.options = options
    self.pathname = os.path.dirname(__file__)
    self.scale = config.get("ui", "scale", float)
    if self.scale < 1.0:
      self.svg_size = '-small'
    else:
      self.svg_size = ''
    # Make lint happy by defining these.
    self.mouse_image = None
    self.alt_image = None
    self.hbox = None
    self.window = None
    self.event_box = None
    self.mouse_indicator_win = None
    self.key_image = None
    self.shift_image = None
    self.ctrl_image = None
    self.meta_image = None
    self.buttons = None

    self.enabled = {
        'MOUSE': config.get("buttons", "mouse", bool),
        'SHIFT': config.get("buttons", "shift", bool),
        'CTRL': config.get("buttons", "ctrl", bool),
        'META': config.get("buttons", "meta", bool),
        'ALT': config.get("buttons", "alt", bool),
    }
    self.emulate_middle = config.get("devices", "emulate_middle", bool)
    self.modmap = mod_mapper.safely_read_mod_map(config.get("devices", "map"))
    self.swap_buttons = config.get("devices", "swap_buttons", bool)

    self.name_fnames = self.create_names_to_fnames()
    self.pixbufs = lazy_pixbuf_creator.LazyPixbufCreator(self.name_fnames,
                                                         self.scale)
    self.devices = xlib.XEvents()
    self.devices.start()

    self.create_window()

  def do_screenshot(self):
    """Create a screenshot showing some keys."""
    import time
    for key in self.options.screenshot.split(','):
      try:
        if key == 'KEY_EMPTY':
          continue
        if key.startswith('KEY_'):
          key_info = self.modmap.get_from_name(key)
          if not key_info:
            print 'Key %s not found' % key
            self.destroy(None)
            return
          scancode = key_info[0]
          event = xlib.XEvent('EV_KEY', scancode=scancode, code=key, value=1)
        elif key.startswith('BTN_'):
          event = xlib.XEvent('EV_KEY', scancode=0, code=key, value=1)

        self.handle_event(event)
        while gtk.events_pending():
          gtk.main_iteration(False)
        time.sleep(0.1)
      except Exception, exp:
        print exp
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
    self.destroy(None)

  def create_names_to_fnames(self):
    """Give a name to images."""
    ftn = {
      'MOUSE': [self.svg_name('mouse'),],
      'BTN_MIDDLE': [self.svg_name('mouse'), self.svg_name('middle-mouse')],
      'SCROLL_UP': [self.svg_name('mouse'), self.svg_name('scroll-up-mouse')],
      'SCROLL_DOWN': [self.svg_name('mouse'), self.svg_name('scroll-dn-mouse')],

      'SHIFT': [self.svg_name('shift')],
      'SHIFT_EMPTY': [self.svg_name('shift'), self.svg_name('whiteout-72')],
      'CTRL': [self.svg_name('ctrl')],
      'CTRL_EMPTY': [self.svg_name('ctrl'), self.svg_name('whiteout-58')],
      'META': [self.svg_name('meta'), self.svg_name('meta')],
      'META_EMPTY': [self.svg_name('meta'), self.svg_name('whiteout-58')],
      'ALT': [self.svg_name('alt')],
      'ALT_EMPTY': [self.svg_name('alt'), self.svg_name('whiteout-58')],
      'KEY_EMPTY': [
          fix_svg_key_closure(self.svg_name('one-char-template'), [('&amp;', '')]),
              self.svg_name('whiteout-48')],
      'BTN_LEFTRIGHT': [
          self.svg_name('mouse'), self.svg_name('left-mouse'), self.svg_name('right-mouse')],
    }
    if self.swap_buttons:
      ftn.update({
        'BTN_RIGHT': [self.svg_name('mouse'), self.svg_name('left-mouse')],
        'BTN_LEFT': [self.svg_name('mouse'), self.svg_name('right-mouse')],
      })
    else:
      ftn.update({
        'BTN_LEFT': [self.svg_name('mouse'), self.svg_name('left-mouse')],
        'BTN_RIGHT': [self.svg_name('mouse'), self.svg_name('right-mouse')],
      })

    if self.scale >= 1.0:
      ftn.update({
        'KEY_SPACE': [
            fix_svg_key_closure(self.svg_name('two-line-wide'),
            [('TOP', 'Space'), ('BOTTOM', '')])],
        'KEY_TAB': [
            fix_svg_key_closure(self.svg_name('two-line-wide'),
            [('TOP', 'Tab'), ('BOTTOM', u'\u21B9')])],
        'KEY_BACKSPACE': [
            fix_svg_key_closure(self.svg_name('two-line-wide'),
            [('TOP', 'Back'), ('BOTTOM', u'\u21fd')])],
        'KEY_RETURN': [
            fix_svg_key_closure(self.svg_name('two-line-wide'),
            [('TOP', 'Enter'), ('BOTTOM', u'\u23CE')])],
        'KEY_CAPS_LOCK': [
            fix_svg_key_closure(self.svg_name('two-line-wide'),
            [('TOP', 'Capslock'), ('BOTTOM', '')])],
      })
    else:
      ftn.update({
        'KEY_SPACE': [
            fix_svg_key_closure(self.svg_name('one-line-wide'), [('&amp;', 'Space')])],
        'KEY_TAB': [
            fix_svg_key_closure(self.svg_name('one-line-wide'), [('&amp;', 'Tab')])],
        'KEY_BACKSPACE': [
            fix_svg_key_closure(self.svg_name('one-line-wide'), [('&amp;', 'Back')])],
        'KEY_RETURN': [
            fix_svg_key_closure(self.svg_name('one-line-wide'), [('&amp;', 'Enter')])],
        'KEY_CAPS_LOCK': [
            fix_svg_key_closure(self.svg_name('one-line-wide'), [('&amp;', 'Capslck')])],
      })
    return ftn

  def create_window(self):
    """Create the main window."""
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

    self.window.set_title('Keyboard Status Monitor')
    width, height = 30 * self.scale, 48 * self.scale
    self.window.set_default_size(int(width), int(height))
    self.window.set_decorated(config.get("ui", "decorated", bool))

    self.mouse_indicator_win = shaped_window.ShapedWindow(self.svg_name('mouse-indicator'))

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
    for _ in range(self.options.old_keys):
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
    self.add_events()

    old_x = config.get('position', 'x', int)
    old_y = config.get('position', 'y', int)
    if old_x != -1 and old_y != -1 and old_x and old_y:
      self.window.move(old_x, old_y)
    self.window.show()

  def svg_name(self, fname):
    """Return an svg filename given the theme, system."""
    fullname = os.path.join(self.pathname, 'themes/%s/%s%s.svg' % (
        config.get("ui", "theme"), fname, self.svg_size))
    if self.svg_size and not os.path.exists(fullname):
      # Small not found, defaulting to large size
      fullname = os.path.join(self.pathname, 'themes/%s/%s.svg' %
                              (config.get("ui", "theme"), fname))
    return fullname

  def add_events(self):
    """Add events for the window to listen to."""
    self.window.connect('destroy', self.destroy)
    self.window.connect('button-press-event', self.button_pressed)
    self.window.connect('configure-event', self._window_moved)
    self.event_box.connect('button_release_event', self.right_click_handler)

    accelgroup = gtk.AccelGroup()
    key, modifier = gtk.accelerator_parse('<Control>q')
    accelgroup.connect_group(key, modifier, gtk.ACCEL_VISIBLE, self.quit_program)
    self.window.add_accel_group(accelgroup)

    if self.options.screenshot:
      gobject.timeout_add(700, self.do_screenshot)
      return

    gobject.idle_add(self.on_idle)

  def button_pressed(self, widget, evt):
    """A mouse button was pressed."""
    if evt.button != 1:
      return True
    widget.begin_move_drag(evt.button, int(evt.x_root), int(evt.y_root), evt.time)
    return True

  def _window_moved(self, widget, unused_event):
    """The window has moved position, save it."""
    x, y = widget.get_position()
    logging.info('Moved window to %d, %d' % (x, y))
    config.set('position', 'x', x)
    config.set('position', 'y', y)

  def on_idle(self):
    """Check for events on idle."""
    event = self.devices.next_event()
    try:
      self.handle_event(event)
    except KeyboardInterrupt:
      self.quit_program()
      return False
    return True  # continue calling

  def handle_event(self, event):
    """Handle an X event."""
    if not event:
      for button in self.buttons:
        button.empty_event()
      return
    if event.type == 'EV_KEY' and event.value in (0, 1):
      if type(event.code) == str:
        if event.code.startswith('KEY'):
          code_num = event.scancode
          self.handle_key(code_num, event.code, event.value)
        elif event.code.startswith('BTN'):
          self.handle_mouse_button(event.code, event.value)
    elif event.type.startswith('EV_REL') and event.code == 'REL_WHEEL':
      self.handle_mouse_scroll(event.value, event.value)

  def _handle_event(self, image, name, code):
    """Handle an event given image and code."""
    if code == 1:
      logging.debug('Switch to %s, code %s' % (name, code))
      image.switch_to(name)
    else:
      image.switch_to_default()


  def handle_key(self, scan_code, xlib_name, value):
    """Handle a keyboard event."""
    code, medium_name, short_name = self.modmap.get_and_check(scan_code,
                                                            xlib_name)
    if not code:
      logging.info('No mapping for scan_code %s', scan_code)
      return
    if self.scale < 1.0 and short_name:
      medium_name = short_name
    logging.debug('Scan code %s, Key %s pressed = %r', scan_code,
                                                       code, medium_name)
    if code in self.name_fnames:
      self._handle_event(self.key_image, code, value)
      return
    if code.startswith('KEY_SHIFT'):
      if self.enabled['SHIFT']:
        self._handle_event(self.shift_image, 'SHIFT', value)
      return
    if code.startswith('KEY_ALT') or code == 'KEY_ISO_LEVEL3_SHIFT':
      if self.enabled['ALT']:
        self._handle_event(self.alt_image, 'ALT', value)
      return
    if code.startswith('KEY_CONTROL'):
      if self.enabled['CTRL']:
        self._handle_event(self.ctrl_image, 'CTRL', value)
      return
    if code.startswith('KEY_SUPER') or code == 'KEY_MULTI_KEY':
      if self.enabled['META']:
        self._handle_event(self.meta_image, 'META', value)
      return
    if code.startswith('KEY_KP'):
      letter = medium_name
      if code not in self.name_fnames:
        template = 'one-char-numpad-template'
        self.name_fnames[code] = [
            fix_svg_key_closure(self.svg_name(template), [('&amp;', letter)])]
      self._handle_event(self.key_image, code, value)
      return
    if code.startswith('KEY_'):
      letter = medium_name
      if code not in self.name_fnames:
        logging.debug('code not in %s', code)
        if len(letter) == 1:
          template = 'one-char-template'
        else:
          template = 'multi-char-template'
        self.name_fnames[code] = [
            fix_svg_key_closure(self.svg_name(template), [('&amp;', letter)])]
      else:
        logging.debug('code in %s', code)
      self._handle_event(self.key_image, code, value)
      return

  def handle_mouse_button(self, code, value):
    """Handle the mouse button event."""
    if self.enabled['MOUSE']:
      if self.emulate_middle and ((self.mouse_image.current == 'BTN_LEFT'
          and code == 'BTN_RIGHT') or
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
      self._handle_event(self.mouse_image, code, value)

    root = gtk.gdk.screen_get_default().get_root_window()
    x, y, _ = root.get_pointer()
    w, h = self.mouse_indicator_win.get_size()
    self.mouse_indicator_win.move(x - w/2, y - h/2)
    if value == 0 and config.get('ui', 'visible-click', bool):
      self.mouse_indicator_win.fade_away()
    return True

  def handle_mouse_scroll(self, direction, unused_value):
    """Handle the mouse scroll button event."""
    if direction > 0:
      self._handle_event(self.mouse_image, 'SCROLL_UP', 1)
    elif direction < 0:
      self._handle_event(self.mouse_image, 'SCROLL_DOWN', 1)
    self.mouse_image.switch_to_default()
    return True

  def quit_program(self, *unused_args):
    """Quit the program."""
    self.devices.stop_listening()
    self.destroy(None)

  def destroy(self, unused_widget, unused_data=None):
    """Also quit the program."""
    self.devices.stop_listening()
    config.cleanup()
    gtk.main_quit()

  def right_click_handler(self, unused_widget, event):
    """Handle the right click button and show a menu."""
    if event.button != 3:
      return

    menu = self.create_context_menu()

    menu.show()
    menu.popup(None, None, None, event.button, event.time)

  def create_context_menu(self):
    """Create a context menu on right click."""
    menu = gtk.Menu()

    toggle_chrome = gtk.CheckMenuItem(_('Window _Chrome'))
    toggle_chrome.set_active(self.window.get_decorated())
    toggle_chrome.connect_object('activate', self.toggle_chrome,
       self.window.get_decorated())
    toggle_chrome.show()
    menu.append(toggle_chrome)

    settings_click = gtk.MenuItem(_('_Settings...'))
    settings_click.connect_object('activate', self.show_settings_dlg, None)
    settings_click.show()
    menu.append(settings_click)

    quitcmd = gtk.MenuItem(_('_Quit\tCtrl-Q'))
    quitcmd.connect_object('activate', self.destroy, None)
    quitcmd.show()

    menu.append(quitcmd)
    return menu

  def toggle_chrome(self, current):
    """Toggle whether the window has chrome or not."""
    self.window.set_decorated(not current)
    config.set('ui', 'decorated', not current)

  def show_settings_dlg(self, unused_arg):
    """Show the settings dialog."""
    dlg = settings.SettingsDialog(self.window)
    dlg.connect('settings-changed', self.settings_changed)
    dlg.show_all()
    dlg.run()
    dlg.destroy()

  def settings_changed(self, unused_dlg):
    """Event received from the settings dialog."""
    self._toggle_a_key(self.mouse_image, 'MOUSE',
        config.get('buttons', 'mouse', bool))
    self._toggle_a_key(self.meta_image, 'META',
        config.get('buttons', 'meta', bool))
    self._toggle_a_key(self.shift_image, 'SHIFT',
        config.get('buttons', 'shift', bool))
    self._toggle_a_key(self.ctrl_image, 'CTRL',
        config.get('buttons', 'ctrl', bool))
    self._toggle_a_key(self.alt_image, 'ALT',
        config.get('buttons', 'ALT', bool))
    if config.get('ui', 'visible-click', bool):
      self.mouse_indicator_win.fade_away()
    self.window.set_decorated(config.get('ui', 'decorated', bool))

  def _toggle_a_key(self, image, name, show):
    """Toggle show/hide a key."""
    if self.enabled[name] == show:
      return
    if show:
      image.showit = True
      self.enabled[name] = True
      image.switch_to_default()
    else:
      image.showit = False
      self.enabled[name] = False
      image.hide()

def show_version():
  """Show the version number and author, used by help2man."""
  print _('Keymon version %s.') % __version__
  print _('Written by %s') % __author__

def main():
  """Run the program."""
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('-s', '--smaller', dest='smaller', default=False, action='store_true',
                    help=_('Make the dialog 25% smaller than normal.'))
  parser.add_option('-l', '--larger', dest='larger', default=False, action='store_true',
                    help=_('Make the dialog 25% larger than normal.'))
  parser.add_option('-m', '--meta', dest='meta', action='store_true',
                    default=config.get('buttons', 'meta', bool),
                    help=_('Show the meta (windows) key.'))
  parser.add_option('--nometa', dest='meta', action='store_false',
                    help=_('Don\'t show the meta (windows) key.'))
  parser.add_option('--mouse', dest='nomouse', action='store_false',
                    default=not config.get('buttons', 'mouse', bool),
                    help=_('Show the mouse.'))
  parser.add_option('--nomouse', dest='nomouse', action='store_true',
                    help=_('Hide the mouse.'))
  parser.add_option('--shift', dest='noshift', action='store_false',
                    default=not config.get('buttons', 'shift', bool),
                    help=_('Show shift key.'))
  parser.add_option('--noshift', dest='noshift', action='store_true',
                    help=_('Don\'t show the shift key.'))
  parser.add_option('--ctrl', dest='noctrl', action='store_false',
                    default=not config.get('buttons', 'ctrl', bool),
                    help=_('Show the ctrl key.'))
  parser.add_option('--noctrl', dest='noctrl', action='store_true',
                    help=_('Hide the ctrl key.'))
  parser.add_option('--alt', dest='noalt', action='store_false',
                    default=not config.get('buttons', 'alt', bool),
                    help=_('Show the alt key.'))
  parser.add_option('--noalt', dest='noalt', action='store_true',
                    help=_('Hide the alt key.'))
  parser.add_option('--scale', dest='scale',
                    default=config.get('ui', 'scale', float),
                    type='float',
                    help=_('Scale the dialog. ex. 2.0 is 2 times larger, 0.5 is '
                           'half the size. Defaults to %default'))
  parser.add_option('--decorated', dest='decorated', action='store_true',
                    default=config.get('ui', 'decorated', bool),
                    help=_('Show decoration'))
  parser.add_option('--notdecorated', dest='decorated', action='store_false',
                    help=_('No decoration'))
  parser.add_option('--visible_click', dest='visible_click', action='store_true',
                    default=config.get('ui', 'visible-click', bool),
                    help=_('Show where you clicked'))
  parser.add_option('--novisible_click', dest='visible_click', action='store_false',
                    help=_('Turn off the visible button clicks.'))
  parser.add_option('--kbdfile', dest='kbd_file',
                    default=config.get('devices', 'map'),
                    help=_('Use this kbd filename instead running xmodmap.'))
  parser.add_option('--swap', dest='swap_buttons', action='store_true',
                    help=_('Swap the mouse buttons.'))
  parser.add_option('--emulate-middle', dest='emulate_middle', action='store_true',
                    help=_('When you press the left, and right mouse buttons at the same time, '
                           'it displays as a middle mouse button click. '))
  parser.add_option('-v', '--version', dest='version', action='store_true',
                    help=_('Show version information and exit.'))
  parser.add_option('-t', '--theme', dest='theme',
                    default=config.get('ui', 'theme'),
                    help=_('The theme to use when drawing status images (ex. "-t apple").'))
  parser.add_option('--list-themes', dest='list_themes', action='store_true',
                    help=_('List available themes'))
  parser.add_option('--old-keys', dest='old_keys', type='int',
                    help=_('How many historical keypresses to show (defaults to %default)'),
                    default=config.get('buttons', 'old-keys', int))

  group = optparse.OptionGroup(parser, _('Developer Options'),
                    _('These options are for developers.'))
  group.add_option('-d', '--debug', dest='debug', action='store_true',
                    help=_('Output debugging information.'))
  group.add_option('--screenshot', dest='screenshot',
                    help=_('Create a "screenshot.png" and exit. '
                    'Pass a comma separated list of keys to simulate (ex. "KEY_A,KEY_LEFTCTRL").'))
  parser.add_option_group(group)

  (options, unused_args) = parser.parse_args()

  if options.version:
    show_version()
    sys.exit(0)
  if options.debug:
    logging.basicConfig(
        level=logging.DEBUG,
        format = '%(filename)s [%(lineno)d]: %(levelname)s %(message)s')
  if options.smaller:
    options.scale = 0.75
  elif options.larger:
    options.scale = 1.25
  if options.list_themes:
    print _('Available themes:')
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
    keymon.quit_program()

if __name__ == '__main__':
  main()
