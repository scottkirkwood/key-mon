#!/usr/bin/env python

"""
    Keyboard Monitor Configuration
    ==============================
    A parser for the keyboard monitor configuration file which saves settings
    between runs. The goal of this configuration system is to not require any
    other dependencies like gconf, be simple and quick to use, and to give
    users an easy way to save setting between runs of the program.
    
    The defaults dict below defines the layout of the configuration file, which
    will be stored in your user directory under ~/.key-mon/config. Getting
    and setting options is simple, and whenever the file needs to be saved
    it will be automatically.
    
        >>> import config
        >>> config.get("ui", "scale", float)
        1.0
        >>> config.get("ui", "theme")
        "apple"
        >>> config.set("ui", "decorated", True)
    
    Remember to properly cast values you read by passing in the casting method.
    If a value does not exist in the configuration file but does exist in the
    defaults dict then the default value will be used. If it exists in neither,
    then an exception is thrown.
    
    You can force a write to happen on the next flush:
    
        >>> config.write()
    
    You can also explicitly cause the write to happen before the next flush if
    you also invoke the following, which should be called before you exit:
    
        >>> config.cleanup()
    
    License
    -------
    Copyright 2009 Daniel G. Taylor <dan@programmer-art.org>

    Permission is hereby granted, free of charge, to any person obtaining a 
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
"""

import gobject
import logging
import os

from ConfigParser import SafeConfigParser

PATH = os.path.expanduser(os.path.join("~", ".config", "key-mon", "config"))

_log = logging.getLogger("config")

# Internal object storing configuration
_config = None

# The default configuration options. These are used when no configuration file
# exists or when an option is requested that doesn't exist or won't cast 
# properly from an existing configuration file.
_defaults = {
    # User interface options
    "ui": {
        "decorated": "0",
        "opacity": "0.9",
        "scale": "1.0",
        "theme": "classic",
    },
    # Button display options
    "buttons": {
        "mouse": "1",
        "shift": "1",
        "ctrl": "1",
        "alt": "1",
        "meta": "0",
        "old-keys": "0",
    },
    # Device behavior options
    "devices": {
        "map": "us.kbd",
        "emulate_middle": "0",
        "swap_buttons": "0",
    },
}


def reset():
    global _config
    _config = SafeConfigParser()

def _create_default(path):
    """
        Create the default configuration file and load it for use.
    """
    global _config
    
    _log.info("Creating default configuration file %r" % PATH)
    
    _config = SafeConfigParser()
    
    for section in _defaults:
        _config.add_section(section)
        for name in _defaults[section]:
            _config.set(section, name, _defaults[section][name])
    
    _config.write(open(PATH, "wb"))

def init():
    """
        Initialize the configuration system. This will automatically be called
        when you load this module. It either reads an existing configuration or
        creates a default one and sets up the timeout to write changes whenever
        you update parts of the configuration to disk.
    """
    global _config
    
    _log.debug("Initializing configuration system")
    
    if not os.path.exists(PATH):
        if not os.path.exists(os.path.dirname(PATH)):
            os.makedirs(os.path.dirname(PATH))
        _create_default(PATH)
    else:
        _config = SafeConfigParser()
        _config.read(PATH)
        
    _config.dirty = False
    gobject.timeout_add(5000, cleanup)

def get(section, name, cast=lambda x: x):
    """
        Get a configuration value. Section and name define what value you want,
        see the defaults dict above for valid values. If cast is given it must
        be a method which takes a single argument and casts it to some other
        type.
        
            >>> config.get("ui", "decorated", bool)
        
    """
    if cast == bool:
        cast = lambda x: bool(int(x))
    
    try:
        value = cast(_config.get(section, name))
    except:
        value = cast(_defaults[section][name])
    
    _log.debug("Getting %s.%s = %s" % (section, name, str(value)))
    
    return value

def set(section, name, value):
    """
        Set a configuration value. Section and name define what you want
        to set; see the defaults dict above for valid values. The value will be
        coerced to a string for storage in the file. Remember that when getting
        the value you must cast it back to what you need.
        
            >>> config.set("ui", "decorated", True)
        
    """
    if type(value) == bool:
        value = int(value)
    
    _log.debug("Setting %s.%s = %s" % (section, name, str(value)))
    
    _config.set(section, name, str(value))
    _config.dirty = True

def write():
    """
        Mark the config as needing to be written. This may be safely called
        any number of times in a short period. The config will be physically
        written out only every e.g. minute to prevent hard drive thrashing.
    """
    global _config
    
    _config.dirty = True

def _write():
    """
        Actually write the config. Used internally.
    """
    _log.debug("Writing config %r" % PATH)
    _config.write(open(PATH, "wb"))
    _config.dirty = False

def cleanup():
    """
        Cleanup the configuration system. Write pending cached data to disk and
        such. After this has been called you may safely exit your application.
    """
    _log.debug("Checking if config needs to be written")
    if _config.dirty:
        _write()

# Automatically initialize the config when this module is loaded
init()
