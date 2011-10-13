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

"""Settings dialog and related functions."""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

import gettext
import gobject
import gtk
import logging
import os

from ConfigParser import SafeConfigParser

LOG = logging.getLogger('settings')

class SettingsDialog(gtk.Dialog):
  """Create a settings/preferences dialog for keymon."""

  __gproperties__ = {}
  __gsignals__ = {
        'settings-changed' : (
          gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
  }

  def __init__(self, unused_view, options):
    gtk.Dialog.__init__(self, title='Preferences', parent=None,
        flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT |
        gtk.WIN_POS_MOUSE,
        buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
    self.options = options
    self.set_default_size(350, 350)
    self.connect('response', self._response)
    self.notebook = gtk.Notebook()
    self.vbox.pack_start(self.notebook)

    buttons = ButtonsFrame(self)
    self.notebook.append_page(buttons, gtk.Label(_('Buttons')))

    misc = MiscFrame(self)
    self.notebook.append_page(misc, gtk.Label(_('Misc')))

    self.notebook.show()
    self.show()

  def settings_changed(self):
    """Emit the settings changed message to parent."""
    self.emit('settings-changed')

  def _response(self, unused_dialog, response_id):
    """Wait for the close response."""
    if response_id == gtk.RESPONSE_CLOSE:
      LOG.info('Close in _Response.')
    self.destroy()

  @classmethod
  def register(cls):
    """Register this class as a Gtk widget."""
    gobject.type_register(SettingsDialog)

class CommonFrame(gtk.Frame):
  """Stuff common to several frames."""
  def __init__(self, settings):
    gtk.Frame.__init__(self)
    self.settings = settings
    self.create_layout()

  def create_layout(self):
    """Do nothing."""
    pass

  def _add_check(self, vbox, title, tooltip, option):
    """Add a check button."""
    check_button = gtk.CheckButton(label=title)
    val = getattr(self.settings.options, option)
    logging.info('got option %s as %s', option, val)
    if val:
      check_button.set_active(True)
    else:
      check_button.set_active(False)
    check_button.connect('toggled', self._toggled, option)
    check_button.set_tooltip_text(tooltip)
    vbox.pack_start(check_button, False, False)

  def _add_dropdown(self, vbox, title, tooltip, opt_lst, option, width_char=-1):
    """Add a drop down box."""
    hbox = gtk.HBox()
    label = gtk.Label(title)
    label.set_tooltip_text(tooltip)
    hbox.pack_start(label, expand=False, fill=False)

    combo = gtk.combo_box_entry_new_text()
    combo.child.set_width_chars(width_char)
    for opt in opt_lst:
      combo.append_text(str(opt))
    val = getattr(self.settings.options, option)
    if isinstance(val, float):
      str_val = '%0.3g' % val
    else:
      str_val = val
    try:
      index = opt_lst.index(str_val)
    except ValueError:
      index = 0
    combo.set_active(index)

    combo.set_tooltip_text(tooltip)
    hbox.pack_start(combo, expand=False, fill=False, padding=10)
    logging.info('got option %s as %s', option, val)
    combo.connect('changed', self._combo_changed, option)

    vbox.pack_start(hbox, expand=False, fill=False)
    return combo

  def _toggled(self, widget, option):
    """The checkbox was toggled."""
    if widget.get_active():
      val = 1
    else:
      val = 0
    self._update_option(option, val, str(val))

  def _combo_changed(self, widget, option):
    """The combo box changed."""
    val = widget.get_active()
    str_val = widget.get_active_text()
    self._update_option(option, val, str_val)

  def _update_option(self, option, val, str_val):
    """Update an option."""
    if str_val.isdigit():
      setattr(self.settings.options, option, val)
      LOG.info('Set option %s to %s' % (option, val))
    else:
      setattr(self.settings.options, option, str_val)
      LOG.info('Set option %s to %s' % (option, str_val))
    self.settings.options.save()
    self.settings.settings_changed()

class MiscFrame(CommonFrame):
  """The miscellaneous frame."""
  def __init__(self, settings):
    CommonFrame.__init__(self, settings)

  def create_layout(self):
    """Create the box's layout."""
    vbox = gtk.VBox()
    self._add_check(
        vbox, 
        _('Swap left-right mouse buttons'),
        _('Swap the left and the right mouse buttons'),
        'swap_buttons')
    self._add_check(
        vbox,
        _('Left+right buttons emulates middle mouse button'),
        _('Clicking both mouse buttons emulates the middle mouse button.'),
       'emulate_middle')
    self._add_check(
        vbox,
        _('Highly visible click'),
        _('Show a circle when the users clicks.'),
        'visible_click')
    self._add_check(
        vbox,
        _('Window decoration'),
        _('Show the normal windows borders'),
        'decorated')
    self._add_check(
        vbox,
        _('Window backgroundless'),
        _('Show only the buttons'),
        'backgroundless')
    self._add_check(
        vbox,
        _('Only key combinations'),
        _('Show a key only when used with a modifier key (like Control)'),
        'only_combo')
    self._add_check(
        vbox,
        _('StickyKeys mode'),
        _('Make modifier keys be sticky'),
        'sticky_mode')

    sizes = ['1.0', '0.6', '0.8', '1.0', '1.2', '1.4', '1.6', '1.8']
    self._add_dropdown(
        vbox,
        _('Scale:'),
        _('How much larger or smaller than normal to make key-mon. '
          'Where 1.0 is normal sized.'),
        sizes, 'scale', 4)

    timeouts = ['0.2', '0.4', '0.5', '0.6', '0.8', '1.0', '1.2',
            '1.4', '1.6', '1.8', '2.0', '2.5', '3.0', '3.5', '4.0']
    self._add_dropdown(
        vbox,
        _('Key timeout:'),
        _('How long before activated key buttons disappear. '
          'Default is 0.5'),
        timeouts, 'key_timeout', 4)

    self._add_dropdown(
        vbox,
        _('Mouse timeout:'),
        _('How long before activated mouse buttons disappear. '
          'Default is 0.2'),
        timeouts, 'mouse_timeout', 4)

    self._add_dropdown(
        vbox,
        _('Highly visible click timeout:'),
        _('How long before highly visible click disappear. '
          'Default is 0.2'),
        timeouts, 'visible_click_timeout', 4)


    self.themes = self.settings.options.themes.keys() 
    self._add_dropdown(
        vbox,
        _('Themes:'),
        _('Which theme of buttons to show (ex. Apple)'),
        self.themes, 'theme')

    self.kbd_files = sorted(list(set(
        os.path.basename(kbd) for kbd in self.settings.options.kbd_files)))
    self._add_dropdown(
        vbox,
        _('Keymap:'),
        _('Which keymap file to use'),
        self.kbd_files, 'kbd_file')
    self.add(vbox)

class ButtonsFrame(CommonFrame):
  """The buttons frame."""
  def __init__(self, settings):
    """Create common frame."""
    CommonFrame.__init__(self, settings)

  def create_layout(self):
    """Create the layout for buttons."""
    vbox = gtk.VBox()

    self._add_check(
        vbox,
        _('_Mouse'),
        _('Show the mouse.'),
        'mouse')
    self._add_check(
        vbox,
        _('_Shift'),
        _('Show the shift key when pressed.'),
        'shift')
    self._add_check(
        vbox,
        _('_Ctrl'),
        _('Show the Control key when pressed.'),
        'ctrl')
    self._add_check(
        vbox,
        _('Meta (_windows keys)'),
        _('Show the Window\'s key (meta key) when pressed.'),
        'meta')
    self._add_check(
        vbox,
        _('_Alt'),
        _('Show the Alt key when pressed.'),
        'alt')
    self._add_dropdown(
        vbox,
        _('Old Keys:'),
        _('When typing fast show more than one key typed.'),
        [0, 1, 2, 3, 4], 'old_keys')
    self.add(vbox)

def _test_settings_changed(unused_widget):
  """Help to test if the settings change message is received."""
  print 'Settings changed'


def manually_run_dialog():
  """Test the dialog without starting keymon."""
  import key_mon

  SettingsDialog.register()
  gettext.install('key_mon', 'locale')
  logging.basicConfig(
      level=logging.DEBUG,
      format = '%(filename)s [%(lineno)d]: %(levelname)s %(message)s')
  options = key_mon.create_options()
  options.read_ini_file('~/.config/key-mon/config')
  dlg = SettingsDialog(None, options)
  dlg.connect('settings-changed', _test_settings_changed)
  dlg.show_all()
  dlg.run()
  return 0

def get_config_dir():
  """Return the base directory of configuration."""
  return os.environ.get('XDG_CONFIG_HOME',
                        os.path.expanduser('~/.config')) + '/key-mon'

def get_config_dirs(kind=''):
  """Return search paths of certain kind of configuration directory."""
  
  return [d \
          for d in (
              os.path.join(get_config_dir(), kind),
              os.path.join(os.path.dirname(os.path.abspath(__file__)), kind)) \
          if os.path.exists(d)]

def get_themes():
  """Return a dict of themes.
    keys are theme names
    values are tuples of (description, path)
      path is where the theme directory located,
      i.e. theme files are path/*.
  """
  theme_dirs = get_config_dirs('themes')
  themes = {}
  for theme_dir in theme_dirs:
    for entry in sorted(os.listdir(theme_dir)):
      try:
        parser = SafeConfigParser()
        theme_config = os.path.join(theme_dir, entry, 'config')
        parser.read(theme_config)
        desc = parser.get('theme', 'description')
        if entry not in themes:
          themes[entry] = (desc, os.path.join(theme_dir, entry))
      except:
        LOG.warning(_('Unable to read theme %r') % (theme_config))
  return themes

def get_kbd_files():
  """Return a list of kbd file paths"""
  config_dirs = get_config_dirs('')
  kbd_files = [
      os.path.join(d, f) \
      for d in config_dirs \
      for f in sorted(os.listdir(d)) if f.endswith('.kbd')]
  return kbd_files
    
if __name__ == '__main__':
  manually_run_dialog()
