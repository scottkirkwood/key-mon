Release Notes
=============
Jun. 13th, 2010 v 1.0
----------------------
* Switched from DBUS to XLib, now it should work in userland and may work with Wacom.
* Moved the key images up one 'pixel' and the mouse left one 'pixel'.
* Preferences dialog.
* Fixed Issue 5, Clicking two mouse buttons at the same time shows only the last one.
* Fixed Issue 20, Typo in help
* Fixed Issue 29. Highlight mouse cursor and mouse click points.  Still needs some loving though.
* Fixed Issue 31, Problem with mouse highlighting.

Apr. 18th, 2009 v 0.16
----------------
* Fixed mouse images a bit.
* Fixed bug 24, Vol+/Vol- swapped.
* Fixed a typo in setup.py.

Dec. 18th, 2009 v 0.15
----------------
* Added --old_keys arguments, which can show quick key combinations better.
  Example: showing VIM keystrokes might be yyd for delete line.

Dec. 11th, 2009 v 0.14.1
------------------
* Fixed Issue 20, typo in help.
* Fixed Issue 19. Show normal key a little bit longer.

Dec. 10th, 2009 v 0.14
----------------
* Created automated build process.
* Screenshots are now created automatically.
* Created debian package.
* Created normal setup.py package.
* Updated the site's documentation.

Dec. 9th, 2009 v 0.12
---------------
* Add the option to switch the left and right mouse buttons. Issue #15
* Add option to hide the Shift, Ctrl, and or Alt buttons Issue #16

Dec. 2nd, 2009 v 0.11
---------------
* Make the scroll up/down less ambiguous.  Issue #14.
* Fixed a bug where it wasn't using the -small version .svg files.
* Fixed issue #10. Capslock key is too large and overflows.

Nov. 30, 2009 v 0.10
---------------
* Bug where unknown keys caused it to crash. Issue #9.

Nov. 30, 2009 v 0.9.2
---------------
* Make key-mon more robust when there's an unknown key.
* Added a few more characters.
* Bash shell script wasn't passing parameters to key-mon.

Nov. 29, 2009 v 0.9.1
---------------
* The zip was missing files and thus didn't run.

Nov. 28, 2009 v 0.9
-------------
* Created a key-mon script to run the program with gksudo if required.
* Support for running from another directory.

Nov. 28, 2009 v 0.9 Features Added Bugs Fixed
---------------------------------
* Different types of keyboards are supported
* You can force key-mon to use your keymap names, more flexible and you can internationalize.

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

