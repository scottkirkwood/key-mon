#!/usr/bin/env python3

import unittest

from . import lazy_pixbuf_creator

class TestOptionItem(unittest.TestCase):
  """Unit tests for the lazy_pixbuf_creator module"""

  def test_resize(self):
      lazy_pixbuf = lazy_pixbuf_creator.LazyPixbufCreator(name_fnames=[], resize=1.5)
    sample = '''prefix <g
         inkscape:label="Layer 1"> suffix'''
    got = lazy_pixbuf._resize(sample)
    self.assertEqual(got, '''prefix <g transform="scale(1.5, 1.5)"
         inkscape:label="Layer 1"> suffix''')

    sample = '''prefix <g
         inkscape:label="Layer 1"
         transform="translate(2, 2)"> suffix'''
    got = lazy_pixbuf._resize(sample)
    self.assertEqual(got, '''prefix <g
         inkscape:label="Layer 1"
         transform="translate(2, 2) scale(1.5, 1.5)"> suffix''')

  def test_resize_svg(self):
    lazy_pixbuf = lazy_pixbuf_creator.LazyPixbufCreator(name_fnames=[], resize=1.5)

    sample = '''prefix <svg
       id="svg1770"
       height="66"
       width="22.2"
       version="1.1"> suffix'''
    got = lazy_pixbuf._resize(sample)
    self.assertEqual(got, '''prefix <svg
       id="svg1770"
       height="99.0"
       width="33.3"
       version="1.1"> suffix''')
