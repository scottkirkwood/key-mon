Release Notes
=============

June 26, 2012 v 1.12
--------------------
* Issue 116, fix command line handling to take precedence over ini settings.

May 15, 2012 v 1.11
-------------------
* Issue 113, copy scroll left, scroll right to other themes.
* Issue 115, fix crashing locale issue (thanks Yu-Jie Lin!).

Apr 29, 2012 v 1.10
-------------------
* Issue 112, support more mouse buttons than just the three.
* Issue 109, options not working. Also fixed Issue 99.

Jan 22, 2012 v 1.9
------------------
* Added three clear themes by Nenad S. Lazich (thanks).
* Fixed issue 101 patch contributed by ernst.bl.
* Fixed issue 102, configurations not saved for meta.
* Fixed issue 103, crash on -s option.

Oct 14th, 2011 v 1.8
--------------------
* Added --loglevel for specifying logging level
* Added Compose key. It now shows in key image.
* Window is no longer showing in taskbar.
* Window is no longer getting focus unless a mouse click on window first. Once
  pointer leaves, it will not accept focus again.
* Default kbdfile is decided by result of setxkbmap.
* Cache shape masks
* Issue 38, add an about box.
* Issue 42, able to change keymap file in settings dialog.
* Issue 45, add --mouse-timeout, --visible-click-timeout, and rename
  --fade-timeout to --key-timeout.
* Issue 46, add --no-press-fadeout for hide the window after inactivity.
* Issue 59, add --sticky for StickyKeys. Note it does not detect your
  environment, it only make modifier keys be sticky when you use this option.
* Fixed issue 77, keysym does not match because Turkish locale setting, 'i'
  character won't be changed case in 'shift'.
* Fixed issue 74, fix old keys doesn't show the correct number of key images.
* Fixed issue 78, mouse image still shows when with --nomouse;
* Fixed issue 84, mouse image shows up when enabled other images.
* Fixed issue 85, avoid undefined option exception.
* Fixed issue 86, fix create_moveresize_window error by manually handle window
  dragging.
* Fixed issue 90, add two Turkish kbd files and missing codes to xlib.c.
* Fixed issue 75, make AltGr show in Alt image place.
* Fixed issue 67, right Windows key does not show.
* Fixed issue 98, not returning abs path for some setups
* Fixed issue 99, settings from command line interfering with settings from
  settings dialog.

August 4th, 2011 v 1.7
----------------------
* Applied patches from Yu-Jie Lin to, have a background-less window and some
  additional bug fixes.

May 29th, 2011 v 1.6.2
----------------------
* Applied donated patch which fixes issues with old keys and does a better job
  when changing settings in the settings dialog.

May 29th, 2011 v 1.6.1
----------------------
* Applied donated patch which allows longer/shorter delays on the keys shown.

Jan 23rd, 2011 v 1.6
--------------------
* Applied patch for Issue 69 (thanks Doug) which allows combinations of
  mouse button clicks to be displayed (ex. left and right buttons clicked
  at the same time).

October 31st, 2010 v 1.5.1
--------------------------
* Applied patch for Issue 63 (thanks stefantalpalaru) which affects
  Python 2.6.6.

October 24th, 2010 v 1.5
------------------------
* With 'highly visible click' now stays down while clicked and dragged around.
  Feature request (Issue) 44.

October 19th, 2010 v 1.4.4
----------------------------
* Fixed issue 61, key-mon was taking 100% of the CPU in the on idle event.
  Added a small amount of sleep so that it gets called less often.

September 24th, 2010 v 1.4.3
----------------------------
* Fixed issue 52 a third time.  The bad merge affected more code than
  I realized.

September 22nd, 2010 v 1.4.2
----------------------------
* Fixed issue 57, options from the command line are sticky which
  isn't normal.
* Fixed issue 52 (again), There was an accidental regression in the code.
* Fixed a unit test.

September 20th, 2010 v 1.4.1
----------------------------
* Fixed issue 51, -l and -s command lines not working.
* Fixed issue 52, fix python 2.5 compatibility.
* Fixed issue 54, cannot list themes with --list-themes.
* Fixed issue 55, not all themes installed.
* Fixed issue 56, --theme=bob is not very tolerant.
* Fixed issue 58, annoying error message caused by opt-parse.
* Added --reset command line option to force everything back to defaults.

September 18th, 2010 v 1.4
----------------------------
* Removed a Python 2.6 only feature so that it remains compatible
  with Python 2.5

August 10th, 2010 v 1.3
-----------------------
* Settings dialog supports changing the themes and scale.
* Add option to show key only when pressed in combination of a modifier.
  Issue 27.
* Issue 50 resolved, changing scale looks OK.
* Updated README and install files.
* Updated the Portuguese translations.
* Added tooltips to the settings dialog.

August 2nd, 2010 v 1.2.7
------------------------
* Fixed some missing keys Issue 49.
* Complete refactoring how options are handled.

July 18th, 2010 v 1.2.6
-----------------------
* Renamed build_all.py to build.py.
* Completed Portuguese translations.

July 15th, 2010 v 1.2.5
-----------------------
* Added some support for internationalization.

July 7th, 2010 v 1.2.4
----------------------
* Added missing librsvg2-common to Debian package.

July 4th, 2010 v 1.2.3
----------------------
* Changed the style to be more PEP 8 compatible.
* Fixed a few small bugs.
* Using new version of pybdist.

June 20th, 2010 v 1.2.2
-----------------------
* Added the correct copyright notices.

June 20th, 2010 v 1.2.1
-----------------------
* Added icon to the Debian install.

June 18th, 2010 v 1.2
---------------------
* Added the man page to the Debian install.
* Build is now super automated.
* Fixed the screenshots.

Jun. 17th, 2010 v 1.1
---------------------
* A little smarter about key names when the keycodes don't seem to match.
* Fixed and improved the Debian install.
* Fixed Issue 25. Darken the mouse buttons.

Jun. 13th, 2010 v 1.0
----------------------
* Switched from DBUS to XLib, now it should work in user-land and may work
  with Wacom.
* Moved the key images up one 'pixel' and the mouse left one 'pixel'.
* Preferences dialog.
* Fixed Issue 5, Clicking two mouse buttons at the same time shows only the
  last one.
* Fixed Issue 20, Typo in help
* Fixed Issue 29. Highlight mouse cursor and mouse click points.  Still needs
  some loving though.
* Fixed Issue 31, Problem with mouse highlighting.

Apr. 18th, 2009 v 0.16
----------------------
* Fixed mouse images a bit.
* Fixed bug 24, Vol+/Vol- swapped.
* Fixed a typo in setup.py.

Dec. 18th, 2009 v 0.15
----------------------
* Added --old_keys arguments, which can show quick key combinations better.
  Example: showing VIM keystrokes might be yyd for delete line.

Dec. 11th, 2009 v 0.14.1
------------------------
* Fixed Issue 20, typo in help.
* Fixed Issue 19. Show normal key a little bit longer.

Dec. 10th, 2009 v 0.14
----------------------
* Created automated build process.
* Screenshots are now created automatically.
* Created Debian package.
* Created normal setup.py package.
* Updated the site's documentation.

Dec. 9th, 2009 v 0.12
---------------------
* Add the option to switch the left and right mouse buttons. Issue #15
* Add option to hide the Shift, Ctrl, and or Alt buttons Issue #16

Dec. 2nd, 2009 v 0.11
---------------------
* Make the scroll up/down less ambiguous.  Issue #14.
* Fixed a bug where it wasn't using the -small version .svg files.
* Fixed issue #10. Capslock key is too large and overflows.

Nov. 30, 2009 v 0.10
--------------------
* Bug where unknown keys caused it to crash. Issue #9.

Nov. 30, 2009 v 0.9.2
---------------------
* Make key-mon more robust when there's an unknown key.
* Added a few more characters.
* Bash shell script wasn't passing parameters to key-mon.

Nov. 29, 2009 v 0.9.1
---------------------
* The zip was missing files and thus didn't run.

Nov. 28, 2009 v 0.9
-------------------
* Created a key-mon script to run the program with gksudo if required.
* Support for running from another directory.

Nov. 28, 2009 v 0.9 Features Added Bugs Fixed
---------------------------------------------
* Different types of keyboards are supported
* You can force key-mon to use your keymap names, more flexible and you can
  internationalize.

Nov. 25 Features Added
----------------------
* Ctrl-Q to quit
* Smaller buttons don't go on two lines
* Use smaller svg files if they exist, more flexible.

Nov. 24 Resizing Feature
------------------------
* Ability to resize the window at the command line.

Nov. 23 Bug fixes, features added
---------------------------------
* Can toggle meta key and mouse, on and off in menu.
* Give a useful error message if sudo required.
* Add support for python 2.4.
* Last key is now centered.

Nov. 22. Initial Release
------------------------
* Meta key support
* Window Chrome toggle on/off in menu
* Images created on the fly from svg.
* Window is always on top by default.
* Window is without chrome, by default.
* Handle common errors.

