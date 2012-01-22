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
__version__ = '1.9'

import logging
import pygtk
pygtk.require('2.0')
import gettext
import gobject
import gtk
import os
import sys
import time
try:
  import xlib
except ImportError:
  print 'Error: Missing xlib, run sudo apt-get install python-xlib'
  sys.exit(-1)

import options
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
      # Quick XML escape fix
      t = t.replace('<', '&lt;')
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
    self.btns = ['MOUSE', 'BTN_RIGHT', 'BTN_MIDDLE', 'BTN_MIDDLERIGHT',
                 'BTN_LEFT', 'BTN_LEFTRIGHT', 'BTN_LEFTMIDDLE',
                 'BTN_LEFTMIDDLERIGHT']
    self.options = options
    self.pathname = os.path.dirname(os.path.abspath(__file__))
    if self.options.scale < 1.0:
      self.svg_size = '-small'
    else:
      self.svg_size = ''
    # Make lint happy by defining these.
    self.hbox = None
    self.window = None
    self.event_box = None
    self.mouse_indicator_win = None
    self.key_image = None
    self.buttons = None

    self.no_press_timer = None

    self.move_dragged = False
    self.shape_mask_current = None
    self.shape_mask_cache = {}

    self.MODS = [u'SHIFT', u'CTRL', u'META', u'ALT']
    self.IMAGES = [u'MOUSE'] + self.MODS
    self.images = dict([(img, None) for img in self.IMAGES])
    self.enabled = dict((img, self.get_option(img.lower())) for img in self.IMAGES)

    self.options.kbd_files = settings.get_kbd_files()
    self.modmap = mod_mapper.safely_read_mod_map(self.options.kbd_file, self.options.kbd_files)

    self.name_fnames = self.create_names_to_fnames()
    self.devices = xlib.XEvents()
    self.devices.start()

    self.pixbufs = lazy_pixbuf_creator.LazyPixbufCreator(self.name_fnames,
                                                         self.options.scale)
    self.create_window()
    self.reset_no_press_timer()

  def get_option(self, attr):
    """Shorthand for getattr(self.options, attr)"""
    return getattr(self.options, attr)

  def do_screenshot(self):
    """Create a screenshot showing some keys."""
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
    if self.options.scale < 1.0:
      self.svg_size = '-small'
    else:
      self.svg_size = ''
    ftn = {
      'MOUSE': [self.svg_name('mouse'),],
      'BTN_MIDDLE': [self.svg_name('mouse'), self.svg_name('middle-mouse')],
      'SCROLL_UP': [self.svg_name('mouse'), self.svg_name('scroll-up-mouse')],
      'SCROLL_DOWN': [self.svg_name('mouse'), self.svg_name('scroll-dn-mouse')],

      'REL_LEFT': [self.svg_name('mouse'), self.svg_name('sroll-lft-mouse')],
      'REL_RIGHT': [self.svg_name('mouse'), self.svg_name('scroll-rgt-mouse')],
      'SHIFT': [self.svg_name('shift')],
      'SHIFT_EMPTY': [self.svg_name('shift'), self.svg_name('whiteout-72')],
      'CTRL': [self.svg_name('ctrl')],
      'CTRL_EMPTY': [self.svg_name('ctrl'), self.svg_name('whiteout-58')],
      'META': [self.svg_name('meta'), self.svg_name('meta')],
      'META_EMPTY': [self.svg_name('meta'), self.svg_name('whiteout-58')],
      'ALT': [self.svg_name('alt')],
      'ALT_EMPTY': [self.svg_name('alt'), self.svg_name('whiteout-58')],
      'ALTGR': [self.svg_name('altgr')],
      'ALTGR_EMPTY': [self.svg_name('altgr'), self.svg_name('whiteout-58')],
      'KEY_EMPTY': [
          fix_svg_key_closure(self.svg_name('one-char-template'), [('&amp;', '')]),
              self.svg_name('whiteout-48')],
      'BTN_LEFTRIGHT': [
          self.svg_name('mouse'), self.svg_name('left-mouse'),
          self.svg_name('right-mouse')],
      'BTN_LEFTMIDDLERIGHT': [
          self.svg_name('mouse'), self.svg_name('left-mouse'),
          self.svg_name('middle-mouse'), self.svg_name('right-mouse')],
    }
    if self.options.swap_buttons:
      # swap the meaning of left and right
      left_str = 'right'
      right_str = 'left'
    else:
      left_str = 'left'
      right_str = 'right'

    ftn.update({
      'BTN_RIGHT': [self.svg_name('mouse'),
        self.svg_name('%s-mouse' % right_str)],
      'BTN_LEFT': [self.svg_name('mouse'),
        self.svg_name('%s-mouse' % left_str)],
      'BTN_LEFTMIDDLE': [
          self.svg_name('mouse'), self.svg_name('%s-mouse' % left_str),
          self.svg_name('middle-mouse')],
      'BTN_MIDDLERIGHT': [
          self.svg_name('mouse'), self.svg_name('middle-mouse'),
          self.svg_name('%s-mouse' % right_str)],
    })

    if self.options.scale >= 1.0:
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
        'KEY_MULTI_KEY': [
            fix_svg_key_closure(self.svg_name('two-line-wide'),
            [('TOP', 'Compose'), ('BOTTOM', '')])],
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
        'KEY_MULTI_KEY': [
            fix_svg_key_closure(self.svg_name('one-line-wide'), [('&amp;', 'Compose')])],
      })
    return ftn

  def create_window(self):
    """Create the main window."""
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_resizable(False)

    self.window.set_title('Keyboard Status Monitor')
    width, height = 30 * self.options.scale, 48 * self.options.scale
    self.window.set_default_size(int(width), int(height))
    self.window.set_decorated(self.options.decorated)

    self.mouse_indicator_win = shaped_window.ShapedWindow(
        self.svg_name('mouse-indicator'),
        timeout=self.options.visible_click_timeout)

    self.mouse_follower_win = shaped_window.ShapedWindow(
        self.svg_name('mouse-follower'))
    if self.options.follow_mouse:
        self.mouse_follower_win.show()

    self.window.set_opacity(self.options.opacity)
    self.window.set_keep_above(True)

    self.event_box = gtk.EventBox()
    self.window.add(self.event_box)
    self.event_box.show()

    self.create_images()

    self.hbox = gtk.HBox(False, 0)
    self.event_box.add(self.hbox)

    self.layout_boxes()
    self.hbox.show()

    self.add_events()

    self.set_accept_focus(False)
    self.window.set_skip_taskbar_hint(True)

    old_x = self.options.x_pos
    old_y = self.options.y_pos
    if old_x != -1 and old_y != -1 and old_x and old_y:
      self.window.move(old_x, old_y)
    self.window.show()

  def update_shape_mask(self, *unused_args, **kwargs):
    if not self.options.backgroundless:
      return
    force = kwargs.get('force', False)

    btns = [btn for btn in self.buttons if btn.get_visible()]
    # Generate id to see if current mask needs to be updated, which is a tuple
    # of allocation of buttons.
    cache_id = tuple(tuple(btn.get_allocation()) for btn in btns)
    if cache_id == self.shape_mask_current and not force:
      return

    # Try to find existing mask in cache
    # TODO limit number of cached masks
    shape_mask = self.shape_mask_cache.get(cache_id, None)
    if shape_mask and not force:
      self.window.shape_combine_mask(shape_mask, 0, 0)
      self.shape_mask_current = cache_id
      return

    _, _, width, height = self.window.get_allocation()
    masks = [self.pixbufs.get(btn.current).render_pixmap_and_mask()[1] \
             for btn in btns]
    shape_mask = gtk.gdk.Pixmap(None, width, height, masks[0].get_depth())

    gc = gtk.gdk.GC(shape_mask)
    # Initialize the mask just in case masks of buttons can't fill the window,
    # if that happens, some artifacts will be seen usually at right edge.
    gc.set_foreground(
        gtk.gdk.Color(pixel=0) if self.options.backgroundless else \
        gtk.gdk.Color(pixel=1))
    shape_mask.draw_rectangle(gc, True, 0, 0, width, height)

    for btn_allocation, mask in zip(cache_id, masks):
      # Don't create mask until every image is allocated
      if btn_allocation[0] == -1:
        return
      shape_mask.draw_drawable(gc, mask, 0, 0, *btn_allocation)

    self.window.shape_combine_mask(shape_mask, 0, 0)
    self.shape_mask_current = cache_id
    self.shape_mask_cache[cache_id] = shape_mask

  def create_images(self):
    self.images['MOUSE'] = two_state_image.TwoStateImage(self.pixbufs, 'MOUSE')
    for img in self.MODS:
      self.images[img] = two_state_image.TwoStateImage(
          self.pixbufs, img + '_EMPTY', self.enabled[img])
    self.create_buttons()

  def create_buttons(self):
    self.buttons = list(self.images[img] for img in self.IMAGES)
    for _ in range(self.options.old_keys):
      key_image = two_state_image.TwoStateImage(self.pixbufs, 'KEY_EMPTY')
      self.buttons.append(key_image)
    self.key_image = two_state_image.TwoStateImage(self.pixbufs, 'KEY_EMPTY')
    self.buttons.append(self.key_image)
    for but in self.buttons:
      if but.normal == 'MOUSE':
        but.timeout_secs = self.options.mouse_timeout
      else:
        but.timeout_secs = self.options.key_timeout
      but.connect('size_allocate', self.update_shape_mask)

  def layout_boxes(self):
    for child in self.hbox.get_children():
      self.hbox.remove(child)
    for img in self.IMAGES:
      if not self.enabled[img]:
        self.images[img].hide()
      self.hbox.pack_start(self.images[img], False, False, 0)

    prev_key_image = None
    for key_image in self.buttons[-(self.options.old_keys + 1):-1]:
#      key_image.hide()
      #key_image.timeout_secs = 0.5
      key_image.defer_to = prev_key_image
      self.hbox.pack_start(key_image, True, True, 0)
      prev_key_image = key_image

    # This must be after the loop above.
    #self.key_image.timeout_secs = 0.5

    self.key_image.defer_to = prev_key_image
    self.hbox.pack_start(self.key_image, True, True, 0)

  def svg_name(self, fname):
    """Return an svg filename given the theme, system."""
    themepath = self.options.themes[self.options.theme][1]
    fullname = os.path.join(themepath, '%s%s.svg' % (fname, self.svg_size))
    if self.svg_size and not os.path.exists(fullname):
      # Small not found, defaulting to large size
      fullname = os.path.join(themepath, '%s.svg' % fname)
    return fullname

  def add_events(self):
    """Add events for the window to listen to."""
    self.window.connect('destroy', self.destroy)
    self.window.connect('button-press-event', self.button_pressed)
    self.window.connect('button-release-event', self.button_released)
    self.window.connect('leave-notify-event', self.pointer_leave)
    self.event_box.connect('button_release_event', self.right_click_handler)

    accelgroup = gtk.AccelGroup()
    key, modifier = gtk.accelerator_parse('<Control>q')
    accelgroup.connect_group(key, modifier, gtk.ACCEL_VISIBLE, self.quit_program)

    key, modifier = gtk.accelerator_parse('<Control>s')
    accelgroup.connect_group(key, modifier, gtk.ACCEL_VISIBLE, self.show_settings_dlg)
    self.window.add_accel_group(accelgroup)

    if self.options.screenshot:
      gobject.timeout_add(700, self.do_screenshot)
      return

    gobject.idle_add(self.on_idle)

  def button_released(self, unused_widget, evt):
    """A mouse button was released."""
    if evt.button == 1:
      self.move_dragged = None
    return True

  def button_pressed(self, widget, evt):
    """A mouse button was pressed."""
    self.set_accept_focus(True)
    if evt.button == 1:
      self.move_dragged = widget.get_pointer()
      self.window.set_opacity(self.options.opacity)
      # remove no_press_timer
      if self.no_press_timer:
        gobject.source_remove(self.no_press_timer)
        self.no_press_timer = None
    return True

  def pointer_leave(self, unused_widget, unused_evt):

    self.set_accept_focus(False)

  def set_accept_focus(self, accept_focus=True):

    self.window.set_accept_focus(accept_focus)
    if accept_focus:
      logging.debug('window now accepts focus')
    else:
      logging.debug('window now does not accept focus')

  def _window_moved(self):
    """The window has moved position, save it."""
    if not self.move_dragged:
      return
    old_p = self.move_dragged
    new_p = self.window.get_pointer()
    x, y = self.window.get_position()
    x, y = x + new_p[0] - old_p[0], y + new_p[1] - old_p[1]
    self.window.move(x, y)

    logging.info('Moved window to %d, %d' % (x, y))
    self.options.x_pos = x
    self.options.y_pos = y

  def on_idle(self):
    """Check for events on idle."""
    event = self.devices.next_event()
    try:
      if event:
        self.handle_event(event)
      else:
        for button in self.buttons:
          button.empty_event()
      time.sleep(0.001)
    except KeyboardInterrupt:
      self.quit_program()
      return False
    return True  # continue calling

  def handle_event(self, event):
    """Handle an X event."""
    if event.type == 'EV_MOV':
      if self.mouse_indicator_win.get_property('visible'):
        self.mouse_indicator_win.center_on_cursor(*event.value)
      if self.mouse_follower_win.get_property('visible'):
        self.mouse_follower_win.center_on_cursor(*event.value)
      if self.move_dragged:
        self._window_moved()
    elif event.type == 'EV_KEY' and event.value in (0, 1):
      if type(event.code) == str:
        if event.code.startswith('KEY'):
          code_num = event.scancode
          self.handle_key(code_num, event.code, event.value)
        elif event.code.startswith('BTN'):
          self.handle_mouse_button(event.code, event.value)
      if not self.move_dragged:
        self.reset_no_press_timer()
    elif event.type.startswith('EV_REL') and event.code == 'REL_WHEEL':
      self.handle_mouse_scroll(event.value, event.value)
    elif event.code.startswith('REL'):
      self.handle_mouse_scroll(event.value, event.value)

  def reset_no_press_timer(self):
    """Initialize no_press_timer"""
    if not self.options.no_press_fadeout:
      return
    logging.debug('Resetting no_press_timer')
    if not self.window.get_property('visible'):
      self.window.move(self.options.x_pos, self.options.y_pos)
      self.window.show()
    self.window.set_opacity(self.options.opacity)
    if self.no_press_timer:
      gobject.source_remove(self.no_press_timer)
      self.no_press_timer = None
    self.no_press_timer = gobject.timeout_add(int(self.options.no_press_fadeout * 1000), self.no_press_fadeout)

  def no_press_fadeout(self, begin=True):
    """Fadeout the window in a second
    Args:
      begin: indicate if this timeout is requested by handle_event.
    """
    opacity = self.window.get_opacity() - self.options.opacity / 10.0
    if opacity < 0.0:
      opacity = 0.0;
    logging.debug('Set opacity = %f' % opacity)
    self.window.set_opacity(opacity)
    if opacity == 0.0:
      self.window.hide()
      # No need to fade out more
      self.no_press_timer = None
      return False

    if begin:
      # Recreate a new timer with 0.1 seccond interval
      self.no_press_timer = gobject.timeout_add(100, self.no_press_fadeout)
      # The current self.options.no_press_fadeout interval will not be timed
      # out again.
      return False

  def _show_down_key(self, name):
    """Show the down key.
    Normally True, unless combo is set.
    Args:
      name: name of the key being held down.
    Returns:
      True if the key should be shown
    """
    if not self.options.only_combo:
      return True
    if self.is_shift_code(name):
      return True
    if (any(self.images[img].is_pressed() for img in self.MODS)):
      return True
    return False

  def _handle_event(self, image, name, code):
    """Handle an event given image and code."""
    image.really_pressed = code == 1
    if code == 1:
      if self._show_down_key(name):
        logging.debug('Switch to %s, code %s' % (name, code))
        image.switch_to(name)
      return

    # on key up
    if self.is_shift_code(name):
      # shift up is always shown
      if not self.options.sticky_mode:
        image.switch_to_default()
      return
    else:
      for img in self.MODS:
        self.images[img].reset_time_if_pressed()
      image.switch_to_default()

  def is_shift_code(self, code):
    if code in ('SHIFT', 'ALT', 'ALTGR', 'CTRL', 'META'):
      return True
    return False

  def handle_key(self, scan_code, xlib_name, value):
    """Handle a keyboard event."""
    code, medium_name, short_name = self.modmap.get_and_check(scan_code,
                                                              xlib_name)
    if not code:
      logging.info('No mapping for scan_code %s', scan_code)
      return
    if self.options.scale < 1.0 and short_name:
      medium_name = short_name
    logging.debug('Scan code %s, Key %s pressed = %r', scan_code,
                                                       code, medium_name)
    if code in self.name_fnames:
      self._handle_event(self.key_image, code, value)
      return
    for keysym, img in (('KEY_SHIFT', 'SHIFT'), ('KEY_CONTROL', 'CTRL'),
                        ('KEY_ALT', 'ALT'), ('KEY_ISO_LEVEL3_SHIFT', 'ALT'),
                        ('KEY_SUPER', 'META')):
      if code.startswith(keysym):
        if self.enabled[img]:
          if keysym == 'KEY_ISO_LEVEL3_SHIFT':
            self._handle_event(self.images['ALT'], 'ALTGR', value)
          else:
            self._handle_event(self.images[img], img, value)
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
      n_image = 0
      n_code = 0
      for i, btn in enumerate(self.btns):
        if btn == code:
          n_code = i
        if btn == self.images['MOUSE'].current:
          n_image = i
      if self.options.emulate_middle and ((self.images['MOUSE'].current == 'BTN_LEFT'
          and code == 'BTN_RIGHT') or
          (self.images['MOUSE'].current == 'BTN_RIGHT' and code == 'BTN_LEFT')):
        code = 'BTN_MIDDLE'
      elif value == 0 and n_code != n_image:
        code = self.btns[n_image - n_code]
      elif value == 1 and n_image:
        code = self.btns[n_image | n_code]
      self._handle_event(self.images['MOUSE'], code, value)

    if self.options.visible_click:
      if value == 1:
        self.mouse_indicator_win.center_on_cursor()
        self.mouse_indicator_win.maybe_show()
      else:
        self.mouse_indicator_win.fade_away()
    return True

  def handle_mouse_scroll(self, direction, unused_value):
    """Handle the mouse scroll button event."""
    if not self.enabled['MOUSE']:
      return
    if direction == 'REL_RIGHT':
      self._handle_event(self.images['MOUSE'], 'REL_RIGHT', 1)
    elif direction == 'REL_LEFT':
      self._handle_event(self.images['MOUSE'], 'REL_LEFT', 1)
    elif direction > 0:
      self._handle_event(self.images['MOUSE'], 'SCROLL_UP', 1)
    elif direction < 0:
      self._handle_event(self.images['MOUSE'], 'SCROLL_DOWN', 1)
    self.images['MOUSE'].switch_to_default()
    return True

  def quit_program(self, *unused_args):
    """Quit the program."""
    self.devices.stop_listening()
    self.destroy(None)

  def destroy(self, unused_widget, unused_data=None):
    """Also quit the program."""
    self.devices.stop_listening()
    self.options.save()
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

    settings_click = gtk.MenuItem(_('_Settings...\tCtrl-S'))
    settings_click.connect_object('activate', self.show_settings_dlg, None)
    settings_click.show()
    menu.append(settings_click)

    about_click = gtk.MenuItem(_('_About...'))
    about_click.connect_object('activate', self.show_about_dlg, None)
    about_click.show()
    menu.append(about_click)

    quitcmd = gtk.MenuItem(_('_Quit\tCtrl-Q'))
    quitcmd.connect_object('activate', self.destroy, None)
    quitcmd.show()

    menu.append(quitcmd)
    return menu

  def toggle_chrome(self, current):
    """Toggle whether the window has chrome or not."""
    self.window.set_decorated(not current)
    self.options.decorated = not self.options.decorated

  def show_settings_dlg(self, *unused_args):
    """Show the settings dialog."""
    dlg = settings.SettingsDialog(self.window, self.options)
    dlg.connect('settings-changed', self.settings_changed)
    dlg.show_all()
    dlg.run()
    dlg.destroy()

  def settings_changed(self, unused_dlg):
    """Event received from the settings dialog."""
    for img in self.IMAGES:
      self._toggle_a_key(self.images[img], img, self.get_option(img.lower()))
    self.create_buttons()
    self.layout_boxes()
    self.mouse_indicator_win.hide()
    self.mouse_indicator_win.timeout = self.options.visible_click_timeout
    self.window.set_decorated(self.options.decorated)
    self.name_fnames = self.create_names_to_fnames()
    self.pixbufs.reset_all(self.name_fnames, self.options.scale)
    for but in self.buttons:
      if but.normal != 'KEY_EMPTY':
        but.reset_image(self.enabled[but.normal.replace('_EMPTY', '')])
      else:
        but.reset_image()
      if but.normal == 'MOUSE':
        but.timeout_secs = self.options.mouse_timeout
      else:
        but.timeout_secs = self.options.key_timeout

    # all this to get it to resize smaller
    x, y = self.window.get_position()
    self.hbox.resize_children()
    self.window.resize_children()
    self.window.reshow_with_initial_size()
    self.hbox.resize_children()
    self.event_box.resize_children()
    self.window.resize_children()
    self.window.move(x, y)
    self.update_shape_mask(force=True)

    # reload keymap
    self.modmap = mod_mapper.safely_read_mod_map(
            self.options.kbd_file, self.options.kbd_files)

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

  def show_about_dlg(self, *_):

    dlg = gtk.AboutDialog()
    # Find the logo file
    logo_paths = (os.path.join(self.pathname, '../../icons'),)
    logo_paths += tuple(logo_path + '/share/pixmaps' for logo_path in (
            os.path.expanduser('~'),
            '/usr', '/usr/local', '/opt/local',
            ))
    logo_paths = [logo_path + '/key-mon.xpm' for logo_path in logo_paths]
    for logo_path in logo_paths:
      if os.path.exists(logo_path):
        dlg.set_logo(gtk.gdk.pixbuf_new_from_file(logo_path))
        break

    dlg.set_name('Keyboard Status Monitor')
    dlg.set_program_name('key-mon')
    dlg.set_website('http://code.google.com/p/key-mon/')
    dlg.set_version(__version__)
    dlg.set_authors([
        __author__,
        'Yu-Jie Lin',
        'Danial G. Taylor',
        'Jakub Steiner',
        ])
    dlg.set_license('''Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.''')
    dlg.run()
    dlg.destroy()

def show_version():
  """Show the version number and author, used by help2man."""
  print _('Keymon version %s.') % __version__
  print _('Written by %s') % __author__

def create_options():
  opts = options.Options()

  opts.add_option(opt_short='-s', opt_long='--smaller', dest='smaller', default=False,
                  type='bool',
                  help=_('Make the dialog 25% smaller than normal.'))
  opts.add_option(opt_short='-l', opt_long='--larger', dest='larger', default=False,
                  type='bool',
                  help=_('Make the dialog 25% larger than normal.'))
  opts.add_option(opt_short='-m', opt_long='--meta', dest='meta', type='bool',
                  ini_group='buttons', ini_name='meta', default=None,
                  help=_('Show the meta (windows) key.'))
  opts.add_option(opt_long='--mouse', dest='mouse', type='bool', default=True,
                  ini_group='buttons', ini_name='mouse',
                  help=_('Show the mouse.'))
  opts.add_option(opt_long='--shift', dest='shift', type='bool', default=True,
                  ini_group='buttons', ini_name='shift',
                  help=_('Show shift key.'))
  opts.add_option(opt_long='--ctrl', dest='ctrl', type='bool', default=True,
                  ini_group='buttons', ini_name='ctrl',
                  help=_('Show the ctrl key.'))
  opts.add_option(opt_long='--alt', dest='alt', type='bool', default=True,
                  ini_group='buttons', ini_name='alt',
                  help=_('Show the alt key.'))
  opts.add_option(opt_long='--scale', dest='scale', type='float', default=1.0,
                  ini_group='ui', ini_name='scale',
                  help=_('Scale the dialog. ex. 2.0 is 2 times larger, 0.5 is '
                         'half the size. Defaults to %default'))
  opts.add_option(opt_long='--key-timeout', dest='key_timeout',
                  type='float', default=0.5,
                  ini_group='ui', ini_name='key_timeout',
                  help=_('Timeout before key returns to unpressed image. '
                         'Defaults to %default'))
  opts.add_option(opt_long='--mouse-timeout', dest='mouse_timeout',
                  type='float', default=0.2,
                  ini_group='ui', ini_name='mouse_timeout',
                  help=_('Timeout before mouse returns to unpressed image. '
                         'Defaults to %default'))
  opts.add_option(opt_long='--visible-click-timeout', dest='visible_click_timeout',
                  type='float', default=0.2,
                  ini_group='ui', ini_name='visible_click_timeout',
                  help=_('Timeout before highly visible click disappears. '
                         'Defaults to %default'))
  opts.add_option(opt_long='--decorated', dest='decorated', type='bool',
                  ini_group='ui', ini_name='decorated',
                  default=False,
                  help=_('Show decoration'))
  opts.add_option(opt_long='--backgroundless', dest='backgroundless', type='bool',
                  ini_group='ui', ini_name='backgroundless',
                  default=False,
                  help=_('Show only buttons'))
  opts.add_option(opt_long='--no-press-fadeout', dest='no_press_fadeout',
                  type='float', default=0.0,
                  ini_group='ui', ini_name='no_press_fadeout',
                  help=_('Fadeout the window after a period with no key press. '
                         'Defaults to %default seconds (Experimental)'))
  opts.add_option(opt_long='--only_combo', dest='only_combo', type='bool',
                  ini_group='ui', ini_name='only_combo',
                  default=False,
                  help=_('Show only key combos (ex. Control-A)'))
  opts.add_option(opt_long='--sticky', dest='sticky_mode', type='bool',
                  ini_group='ui', ini_name='sticky_mode',
                  default=False,
                  help=_('Sticky mode'))
  opts.add_option(opt_long='--visible_click', dest='visible_click', type='bool',
                  ini_group='ui', ini_name='visible-click',
                  default=False,
                  help=_('Show where you clicked'))
  opts.add_option(opt_long='--follow_mouse', dest='follow_mouse', type='bool',
                  ini_group='ui', ini_name='follow-mouse',
                  default=False,
                  help=_('Show the mouse more visibly'))
  opts.add_option(opt_long='--kbdfile', dest='kbd_file',
                  ini_group='devices', ini_name='map',
                  default=None,
                  help=_('Use this kbd filename.'))
  opts.add_option(opt_long='--swap', dest='swap_buttons', type='bool',
                  default=False,
                  ini_group='devices', ini_name='swap_buttons',
                  help=_('Swap the mouse buttons.'))
  opts.add_option(opt_long='--emulate-middle', dest='emulate_middle', type='bool',
                  default=False,
                  ini_group='devices', ini_name='emulate_middle',
                  help=_('When you press the left, and right mouse buttons at the same time, '
                         'it displays as a middle mouse button click. '))
  opts.add_option(opt_short='-v', opt_long='--version', dest='version', type='bool',
                  help=_('Show version information and exit.'))
  opts.add_option(opt_short='-t', opt_long='--theme', dest='theme', type='str',
                  ini_group='ui', ini_name='theme', default='classic',
                  help=_('The theme to use when drawing status images (ex. "-t apple").'))
  opts.add_option(opt_long='--list-themes', dest='list_themes', type='bool',
                  help=_('List available themes'))
  opts.add_option(opt_long='--old-keys', dest='old_keys', type='int',
                  ini_group='buttons', ini_name='old-keys',
                  help=_('How many historical keypresses to show (defaults to %default)'),
                  default=0)
  opts.add_option(opt_long='--reset', dest='reset', type='bool',
                  help=_('Reset all options to their defaults.'),
                  default=None)

  opts.add_option(opt_short=None, opt_long='--opacity', type='float',
                  dest='opacity', default=1.0, help='Opacity of window',
                  ini_group='ui', ini_name='opacity')
  opts.add_option(opt_short=None, opt_long=None, type='int',
                  dest='x_pos', default=-1, help='Last X Position',
                  ini_group='position', ini_name='x')
  opts.add_option(opt_short=None, opt_long=None, type='int',
                  dest='y_pos', default=-1, help='Last Y Position',
                  ini_group='position', ini_name='y')

  opts.add_option_group(_('Developer Options'), _('These options are for developers.'))
  opts.add_option(opt_long='--loglevel', dest='loglevel', type='str', default='',
                  help=_('Logging level'))
  opts.add_option(opt_short='-d', opt_long='--debug', dest='debug', type='bool',
                  default=False,
                  help=_('Output debugging information. '
                         'Shorthand for --loglevel=debug'))
  opts.add_option(opt_long='--screenshot', dest='screenshot', type='str', default='',
                  help=_('Create a "screenshot.png" and exit. '
                         'Pass a comma separated list of keys to simulate'
                         '(ex. "KEY_A,KEY_LEFTCTRL").'))
  return opts


def main():
  """Run the program."""
  # Check for --loglevel, --debug, we deal with them by ourselves because
  # option parser also use logging.
  loglevel = None
  for idx, arg in enumerate(sys.argv):
    if '--loglevel' in arg:
      if '=' in arg:
        loglevel = arg.split('=')[1]
      else:
        loglevel = sys.argv[idx + 1]
      level = getattr(logging, loglevel.upper(), None)
      if level is None:
          raise ValueError('Invalid log level: %s' % loglevel)
      loglevel = level
  else:
    if '--debug' in sys.argv or '-d' in sys.argv:
      loglevel = logging.DEBUG
  logging.basicConfig(
      level=loglevel,
      format='%(filename)s [%(lineno)d]: %(levelname)s %(message)s')
  if loglevel is None:
    # Disabling warning, info, debug messages
    logging.disable(logging.WARNING)

  opts = create_options()
  opts.read_ini_file(os.path.join(settings.get_config_dir(), 'config'))
  desc = _('Usage: %prog [Options...]')
  opts.parse_args(desc)

  if opts.version:
    show_version()
    sys.exit(0)
  if opts.smaller:
    opts.scale = 0.75
  elif opts.larger:
    opts.scale = 1.25

  opts.themes = settings.get_themes()
  if opts.list_themes:
    print _('Available themes:')
    print
    theme_names = sorted(opts.themes)
    name_len = max(len(name) for name in theme_names)
    for theme in theme_names:
      print (' - %%-%ds: %%s' % name_len) % (theme, opts.themes[theme][0])
    raise SystemExit()
  elif opts.theme and opts.theme not in opts.themes:
    print _('Theme %r does not exist') % opts.theme
    print
    print _('Please make sure %r can be found in '
            'one of the following directories:') % opts.theme
    print
    for theme_dir in settings.get_config_dirs('themes'):
      print ' - %s' % theme_dir
    sys.exit(-1)
  if opts.reset:
    print _('Resetting to defaults.')
    opts.reset_to_defaults()
    opts.save()
  keymon = KeyMon(opts)
  try:
    gtk.main()
  except KeyboardInterrupt:
    keymon.quit_program()

if __name__ == '__main__':
  #import cProfile
  #cProfile.run('main()', 'keymonprof')
  main()
