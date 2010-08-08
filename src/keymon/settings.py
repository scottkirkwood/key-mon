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

"""Settings dialog."""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

import gettext
import gobject
import gtk
import logging
import os

LOG = logging.getLogger('settings')

class SettingsDialog(gtk.Dialog):
  """Create a settings/preferences dialog for keymon."""

  __gproperties__ = {}
  __gsignals__ = {
        'settings-changed' : (
          gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
  }

  def __init__(self, view, options):
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

  def _add_check(self, vbox, title, option):
    """Add a check button."""
    check_button = gtk.CheckButton(label=title)
    val = getattr(self.settings.options, option)
    logging.info('got option %s as %s', option, val)
    if val:
      check_button.set_active(True)
    else:
      check_button.set_active(False)
    check_button.connect('toggled', self._toggled, option)
    vbox.pack_start(check_button, False, False)

  def _add_dropdown(self, vbox, title, opt_lst, option):
    """Add a dropdown box."""
    hbox = gtk.HBox()
    label = gtk.Label(title)
    hbox.pack_start(label, expand=False, fill=False)

    combo = gtk.combo_box_new_text()
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

    hbox.pack_start(combo, expand=False, fill=False, padding=10)
    logging.info('got option %s as %s', option, val)
    combo.connect('changed', self._combo_changed, option)

    vbox.pack_start(hbox, expand=False, fill=False)

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
    self._add_check(vbox, _('Swap left-right mouse buttons'), 'swap_buttons')
    self._add_check(vbox, _('Left+right buttons emulates middle mouse button'),
       'emulate_middle')
    self._add_check(vbox, _('Highly visible click'), 'visible_click')
    self._add_check(vbox, _('Window decoration'), 'decorated')

    sizes = ['0.5', '0.75', '0.8', '1.0', '1.25', '1.5', '1.75', '2.5', '3.0']
    self._add_dropdown(vbox, _('Scale:'), sizes, 'scale')

    self.themes = []
    theme_dir = os.path.join(os.path.dirname(__file__), 'themes')
    self.themes = os.listdir(theme_dir)
    self._add_dropdown(vbox, _('Themes:'), self.themes, 'theme')
    self.add(vbox)

class ButtonsFrame(CommonFrame):
  """The buttons frame."""
  def __init__(self, settings):
    """Create common frame."""
    CommonFrame.__init__(self, settings)

  def create_layout(self):
    """Create the layout for buttons."""
    vbox = gtk.VBox()

    self._add_check(vbox, _('_Mouse'), 'mouse')
    self._add_check(vbox, _('_Shift'), 'shift')
    self._add_check(vbox, _('_Ctrl'), 'ctrl')
    self._add_check(vbox, _('Meta (_windows keys)'), 'meta')
    self._add_check(vbox, _('_Alt'), 'alt')
    self._add_dropdown(vbox, _('Old Keys:'), [0, 1, 2, 3, 4], 'old_keys')
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

if __name__ == '__main__':
  manually_run_dialog()
