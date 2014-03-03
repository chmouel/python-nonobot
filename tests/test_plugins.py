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
import shutil
import nonobot.plugins
import tempfile
import unittest

SAMPLE_ARGUMENT_PLUGIN = """
def _arguments(o):
    o.add_option('--blah')
"""

SAMPLE_PLUGIN_METHOD = """
class Plugin:
    def __init__(self, config):
        pass
    def foo(self, line):
        pass
    def foo_doc(self, line):
        "THIS IS SOME DOC"
        pass
"""

class PluginTest(unittest.TestCase):
    def test_get_all_plugin_modules(self):
        try:
            path = tempfile.mkdtemp()
            test_file = path + "/t1.py"
            open(test_file, 'w').write("")
            test_file2 = path + "/t2.py"
            open(test_file2, 'w').write("")
            ret = [x for x in nonobot.plugins.get_all_plugin_modules(path)]
            self.assertEqual(len(ret), 2)
        finally:
            try:
                shutil.rmtree(path)
            except OSError as exc:
                if exc.errno != 2:
                    raise

    def test_get_all_plugin_modules_only_py(self):
        try:
            path = tempfile.mkdtemp()
            test_file = path + "/t1.rb"
            open(test_file, 'w').write("")
            test_file2 = path + "/t2.py"
            open(test_file2, 'w').write("")
            ret = [x for x in nonobot.plugins.get_all_plugin_modules(path)]
            self.assertEqual(len(ret), 1)
        finally:
            try:
                shutil.rmtree(path)
            except OSError as exc:
                if exc.errno != 2:
                    raise

    def test_get_all_plugin_modules_no__init__(self):
        try:
            path = tempfile.mkdtemp()
            test_file = path + "__init__.py"
            open(test_file, 'w').write("")
            test_file2 = path + "/t2.py"
            open(test_file2, 'w').write("")
            ret = [x for x in nonobot.plugins.get_all_plugin_modules(path)]
            self.assertEqual(len(ret), 1)
        finally:
            try:
                shutil.rmtree(path)
            except OSError as exc:
                if exc.errno != 2:
                    raise

    def test_plugin_add_extra_options(self):
        try:
            path = tempfile.mkdtemp()
            test_file = path + "/t1.py"
            open(test_file, 'w').write(SAMPLE_ARGUMENT_PLUGIN)
            optp = optparse.OptionParser()
            nonobot.plugins.plugins_add_extra_options(path, optp)
            self.assertTrue(optp.has_option('--blah'))
        finally:
            try:
                shutil.rmtree(path)
            except OSError as exc:
                if exc.errno != 2:
                    raise
    def test_plugin_add_extra_options(self):
        try:
            path = tempfile.mkdtemp()
            test_file = path + "/t1.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_METHOD)
            optp = optparse.OptionParser()
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            self.assertEquals(len(plugins), 1)
            first_plugin = plugins[plugins.keys()[0]]
            self.assertEquals(len(first_plugin), 2)
            self.assertIn('foo', first_plugin)
            self.assertIn('foo_doc', first_plugin)
            self.assertEqual(first_plugin['foo_doc']['doc'],
                             'THIS IS SOME DOC')
        finally:
            try:
                shutil.rmtree(path)
            except OSError as exc:
                if exc.errno != 2:
                    raise
