#!/usr/bin/python
#
# Copyright 2010 Scott Kirkwood All Rights Reserved.

"""Settings dialog."""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

import gobject
import gtk
import config
import gettext
import logging

_log = logging.getLogger('settings')

class SettingsDialog(gtk.Dialog):
  __gproperties__ = {}
  __gsignals__ = {
        'settings-changed' : (
          gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
  }

  """Preferences dialog."""
  def __init__(self, view):
    gtk.Dialog.__init__(self, title='Preferences', parent=view,
        flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
        buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
    self.set_default_size(350, 350)
    self.connect('response', self._Response)
    self.notebook = gtk.Notebook()
    self.vbox.pack_start(self.notebook)

    bu = ButtonsFrame(self)
    self.notebook.append_page(bu, gtk.Label(_('Buttons')))

    misc = MiscFrame(self)
    self.notebook.append_page(misc, gtk.Label(_('Misc')))

    self.notebook.show()
    self.show()

  def SettingsChanged(self):
    self.emit('settings-changed')

  def _Response(self, dialog, response_id):
    if response_id == gtk.RESPONSE_CLOSE:
      _log.info('Close in _Response.')
      pass
    self.destroy()

  @classmethod
  def Register(self):
    """Register this class as a Gtk widget."""
    gobject.type_register(SettingsDialog)

class CommonFrame(gtk.Frame):
  def __init__(self, settings):
    gtk.Frame.__init__(self)
    self.settings = settings
    self.CreateLayout()

  def CreateLayout(self):
    pass

  def _AddCheck(self, vbox, title, option, sub_option):
    bt = gtk.CheckButton(label=title)
    val = config.get(option, sub_option, bool)
    logging.info('got option %s/%s as %s' % (option, sub_option, val))
    if val:
      bt.set_active(True)
    else:
      bt.set_active(False)
    bt.connect('toggled', self._Toggled, option, sub_option)
    vbox.pack_start(bt, False, False)

  def _AddDropdown(self, vbox, title, opt_lst, option, sub_option):
    hbox = gtk.HBox()
    label = gtk.Label(title)
    hbox.pack_start(label, expand=False, fill=False)

    combo = gtk.combo_box_new_text()
    for opt in opt_lst:
      combo.append_text(str(opt))
    val = config.get(option, sub_option, int)
    combo.set_active(val)
    hbox.pack_start(combo, expand=False, fill=False, padding=10)
    logging.info('got option %s/%s as %s' % (option, sub_option, val))
    combo.connect('changed', self._ComboChanged, option, sub_option)

    vbox.pack_start(hbox, expand=False, fill=False)

  def _Toggled(self, widget, option, sub_option):
    if widget.get_active():
      val = 1
    else:
      val = 0
    self._UpdateOption(option, sub_option, val)

  def _ComboChanged(self, widget, option, sub_option):
    val = widget.get_active()
    self._UpdateOption(option, sub_option, val)

  def _UpdateOption(self, option, sub_option, val):
    config.set(option, sub_option, val)
    config.write()
    config.cleanup()
    _log.info('Set option %s/%s to %s' % (option, sub_option, val))
    self.settings.SettingsChanged()

class MiscFrame(CommonFrame):
  def __init__(self, settings):
    CommonFrame.__init__(self, settings)

  def CreateLayout(self):
    vbox = gtk.VBox()
    self._AddCheck(vbox, _('Swap left-right mouse buttons'), 'devices', 'swap_buttons')
    self._AddCheck(vbox, _('Left+right buttons emulates middle mouse button'),
       'devices', 'emulate_middle')
    self._AddCheck(vbox, _('Highly visible click'), 'ui', 'visible-click')
    self._AddCheck(vbox, _('Window decoration'), 'ui', 'decorated')
    self.add(vbox)

class ButtonsFrame(CommonFrame):
  def __init__(self, settings):
    CommonFrame.__init__(self, settings)

  def CreateLayout(self):
    vbox = gtk.VBox()

    self._AddCheck(vbox, _('_Mouse'), 'buttons', 'mouse')
    self._AddCheck(vbox, _('_Shift'), 'buttons', 'shift')
    self._AddCheck(vbox, _('_Ctrl'), 'buttons', 'ctrl')
    self._AddCheck(vbox, _('Meta (_windows keys)'), 'buttons', 'meta')
    self._AddCheck(vbox, _('_Alt'), 'buttons', 'alt')
    self._AddDropdown(vbox, _('Old Keys:'), [0, 1, 2, 3, 4], 'buttons', 'old-keys')
    self.add(vbox)

def TestSettingsChanged(widget):
  print widget
  print 'Settings changed'

def Main():
  SettingsDialog.Register()
  gettext.install('key_mon', 'locale')
  logging.basicConfig(
      level=logging.DEBUG,
      format = '%(filename)s [%(lineno)d]: %(levelname)s %(message)s')
  dlg = SettingsDialog(None)
  dlg.connect('settings-changed', TestSettingsChanged)
  dlg.show_all()
  dlg.run()
  return 0

if __name__ == '__main__':
  Main()
