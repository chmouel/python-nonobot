# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import optparse
import unittest

import nonobot.plugins
import tests.fixtures as fix
import tests.sample1
import tests.sample2


class PluginTest(unittest.TestCase):
    def test_get_all_plugin_modules(self):
        plugin_manager = fix.make_plugins()
        plugins = plugin_manager.get_methods({'foo: bar'})
        self.assertIn('help', plugins)
        self.assertEqual(len(plugins), 3)

    def test_plugin_add_extra_options(self):
        optp = optparse.OptionParser()
        plugin_manager = fix.make_plugins()
        plugin_manager.add_extra_options(optp)
        self.assertTrue(optp.has_option('--blah'))

    def test_plugin_methods(self):
        plugin_manager = fix.make_plugins(allplugins=(tests.sample1,))
        plugins = plugin_manager.get_methods({'foo: bar'})
        self.assertEqual(len(plugins), 2)
        for i in plugins:
            if type(i) != str:
                first_plugin = plugins[i]
        self.assertEqual(len(first_plugin), 4)
        self.assertIn('foo', first_plugin)
        self.assertIn('foo_doc', first_plugin)
        self.assertEqual(first_plugin['foo_doc']['doc'],
                         'THIS IS SOME DOC')
        self.assertIn('help', plugins)
        self.assertEqual(len(plugins['help']), 1)
        self.assertEqual(plugins['help'],
                         ['[sample1] foo_doc: THIS IS SOME DOC'])

    def test_plugin_stream_method(self):
        plugin_manager = fix.make_plugins(allplugins=(tests.sample2,))
        plugins = plugin_manager.get_methods({'foo: bar'})
        self.assertEqual(len(plugins), 2)
        for i in plugins:
            if type(i) != str:
                first_plugin = plugins[i]
        self.assertEqual(len(first_plugin), 4)
        self.assertIn('stream', first_plugin)
        self.assertEqual(first_plugin['stream']['doc'],
                         'DOC STREAM.')
        self.assertIn('help', plugins)
        self.assertEqual(len(plugins['help']), 2)
        rethelp = ['[sample2] foo2_doc: THIS IS SOME DOC',
                   '[sample2] DOC STREAM.']
        self.assertEqual(plugins['help'], rethelp)

    def test_plugin_class(self):
        config = {'hello': 'moto'}
        cl = nonobot.plugins.Base(config)
        self.assertIn('hello', cl.config)
