#!/usr/bin/env python3
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

import io
import unittest

from . import options

class TestOptionItem(unittest.TestCase):
  """Unit tests for the option module"""
  def test_create_int(self):
    x = options.OptionItem(
        dest='x', _type='int', default=-99,
        name='namex', help='helpx',
        opt_group='opt-group', opt_short='-x', opt_long='--xlong',
        ini_group='ini_group', ini_name='ini_name')
    self.assertEqual(x.value, -99)
    x.value = 2
    self.assertEqual(x.value, 2)
    self.assertEqual(x.type, 'int')
    self.assertEqual(x.name, 'namex')
    self.assertEqual(x.help, 'helpx')
    self.assertEqual(x.opt_group, 'opt-group')
    self.assertEqual(x.opt_short, '-x')
    self.assertEqual(x.opt_long, '--xlong')
    self.assertEqual(x.ini_group, 'ini_group')
    self.assertEqual(x.ini_name, 'ini_name')

  def test_create_bool_false(self):
    x = options.OptionItem(
        dest='x', _type='bool', default=False,
        name='namex', help='helpx',
        opt_group='opt-group', opt_short='-x', opt_long='--xlong',
        ini_group='group', ini_name='section')
    self.assertFalse(x.value)
    x.value = True
    self.assertTrue(x.value)
    x.value = 0
    self.assertFalse(x.value)
    x.value = 1
    self.assertTrue(x.value)
    x.value = None
    self.assertEqual(x.value, None)
    x.value = 'TrUe'
    self.assertTrue(x.value)
    x.value = 'FaLsE'
    self.assertFalse(x.value)
    x.value = 'On'
    self.assertTrue(x.value)
    x.value = 'off'
    self.assertFalse(x.value)
    x.value = 'yeS'
    self.assertTrue(x.value)
    x.value = 'no'
    self.assertFalse(x.value)

  def test_create_bool_none(self):
    x = options.OptionItem(
        opt_short='-x', opt_long='--xx', ini_group='group', ini_name='section',
        dest='x', name='variable', help='variable help', _type='bool',
        default=None)
    self.assertEqual(x.value, None)
    x.value = 0
    self.assertFalse(x.value)
    x.value = 1
    self.assertTrue(x.value)

class TestOptions(unittest.TestCase):
  def setUp(self):
    self.options = options.Options()
    self.options.add_option(
        'x', 'bool', None,
        name='x variable', help='Help Varaible',
        opt_short='-x', opt_long='--xx',
        ini_group='options', ini_name='x')
    self.options.add_option(
        'tr', 'bool', True,
        name='def true', help='Defaults to true',
        opt_short='-t', opt_long='--true',
        ini_group='options', ini_name='true')
    self.options.add_option(
        'fa', 'bool', False,
        name='false variable', help='Defaults to false',
        opt_short='-f', opt_long='--false',
        ini_group='options', ini_name='false')
    self.options.add_option(
        'num', 'int', None,
        name='num none', help='Number that returns None by default',
        opt_short='-n', opt_long='--num',
        ini_group='ints', ini_name='num')
    self.options.add_option(
        'num99', 'int', 99,
        name='num 99', help='Number that defaults to 99',
        opt_short=None, opt_long='--num99',
        ini_group='ints', ini_name='num99')

  def test_optparse(self):
    args = ['-x', '--true', '--num', '123']
    self.options.parse_args("Usage:", args)
    opts = self.options
    self.assertTrue(opts.x)
    self.assertTrue(opts.tr)
    self.assertFalse(opts.fa)
    self.assertEqual(opts.num, 123)
    self.assertEqual(opts.num99, 99)

  def test_from_ini(self):
    lines = []
    lines.append('[ints]')
    lines.append('num99 = 932')
    lines.append('num = 345')
    lines.append('')
    lines.append('[options]')
    lines.append('x = 0')
    lines.append('true = 0')
    lines.append('false = 1')
    io_result = io.StringIO('\n'.join(lines))
    self.options.parse_ini(io_result)
    self.options.parse_args("Usage", [])

    opts = self.options
    self.assertFalse(opts.x)
    self.assertFalse(opts.tr)
    self.assertTrue(opts.fa)
    self.assertEqual(opts.num, 345)
    self.assertEqual(opts.num99, 932)

  def test_override_ini(self):
    lines = []
    lines.append('[ints]')
    lines.append('num99 = 932')
    lines.append('num = 345')
    lines.append('')
    lines.append('[options]')
    lines.append('x = 0')
    lines.append('true = 0')
    lines.append('false = 1')
    io_result = io.StringIO('\n'.join(lines))
    self.options.parse_ini(io_result)
    args = [
        '--num99', '99',
        '--num', '456',
        '--true',
        '-x',
        '--nofalse',
    ]
    self.options.parse_args("Usage", args)

    opts = self.options
    self.assertTrue(opts.x)
    self.assertTrue(opts.tr)
    self.assertFalse(opts.fa)
    self.assertEqual(opts.num, 456)
    self.assertEqual(opts.num99, 99)

  def test_to_ini_empty(self):
    io_result = io.StringIO()
    self.options.write_ini(io_result)
    contents = io_result.getvalue()
    lines = []
    lines.append('[options]')
    lines.append('true = 1')
    lines.append('false = 0')
    lines.append('')
    lines.append('[ints]')
    lines.append('num99 = 99')
    lines.append('')
    lines.append('')
    self.assertEqual('\n'.join(lines), contents)

if __name__ == '__main__':
  unittest.main()
