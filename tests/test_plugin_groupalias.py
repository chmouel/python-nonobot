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
import cPickle
import optparse
import os
import tempfile
import unittest

import nonobot.plugins.groupalias


class FakeConfig(object):
    def __init__(self, tempf):
        try:
            self.group_file = tempf.name
        except(AttributeError):
            self.group_file = tempf


class PluginTest(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        if not self.temp_file.close_called:
            self.temp_file.close()
        os.remove(self.temp_file.name)

    def test_passed_arguments(self):
        optp = optparse.OptionParser()
        ret = nonobot.plugins.groupalias._arguments(optp)
        self.assertTrue(ret.has_option('-g'))

    def test_groupalias_init_config_file_set(self):
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        self.assertEqual(plug.group_file, self.temp_file.name)

    def test_groupalias_init_no_config_file_get_global(self):
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(""))
        self.assertEqual(plug.group_file,
                         nonobot.plugins.groupalias.GROUPS_PICKLE)

    def test_groupalias_init_empty_files_nothing(self):
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        self.assertEqual(plug._groups, {})

    def test_groupalias_init_load_groups(self):
        groups = {'foo': ['bar', 'linux']}
        cPickle.dump(groups, self.temp_file)
        self.temp_file.close()

        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        self.assertEqual(plug._groups, groups)

    def test_alias_no_msg_return(self):
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        self.assertIsNone(plug.alias({'body': ''}))

    def test_alias(self):
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        alias = 'foo'
        aliases = ['bar', 'linux']
        msg = {'body': 'foo bar linux'}
        ret = plug.alias(msg)
        self.assertEqual('%s has been set to %s' % (alias, " ".join(aliases)),
                         ret)
        self.temp_file.close()
        whatsaved = cPickle.load(open(self.temp_file.name, 'r'))
        self.assertEqual({alias: aliases}, whatsaved)

    def test_add(self):
        alias = 'foo'
        aliases = ['bar']
        newalias = 'linux'
        cPickle.dump({alias: aliases}, self.temp_file)
        self.temp_file.close()

        msg = {'body': "%s %s" % (alias, newalias)}
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        ret = plug.add(msg)
        self.assertEqual("%s aliases has been added to %s" % (newalias, alias),
                         ret)

        whatsaved = cPickle.load(open(self.temp_file.name, 'r'))
        self.assertEqual({alias: aliases + [newalias]}, whatsaved)

    def test_delete(self):
        alias = 'foo'
        aliases = ['bar', 'linux']
        cPickle.dump({alias: aliases}, self.temp_file)
        self.temp_file.close()

        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        msg = {'body': alias}
        ret = plug.delete(msg)
        self.assertEqual(ret, '%s has been deleted' % alias)

        whatsaved = cPickle.load(open(self.temp_file.name, 'r'))
        self.assertEqual({}, whatsaved)

    def test_list(self):
        alias = 'foo'
        aliases = ['bar', 'linux']
        cPickle.dump({alias: aliases}, self.temp_file)
        self.temp_file.close()

        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        ret = plug.list(alias)
        self.assertEqual(ret[0], 'alias foo => bar, linux')

    def test_list_no_alias_there(self):
        group = 'foo'
        newalias = 'bar'
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        msg = {'body': "%s %s" % (group, newalias)}
        ret = plug.add(msg)
        self.assertEqual("group %s has not been defined yet use alias" % group,
                         ret)

    def test_stream_no_alias_ret(self):
        alias = 'foo'
        aliases = ['bar', 'linux']
        cPickle.dump({alias: aliases}, self.temp_file)
        self.temp_file.close()

        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        ret = plug.stream({'body': "@unknown hola que tal"})
        self.assertIsNone(ret)

    def test_stream(self):
        alias = 'foo'
        aliases = ['bar', 'linux']
        phrase = 'hello ca va?'
        cPickle.dump({alias: aliases}, self.temp_file)
        self.temp_file.close()

        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        msg = {'body': "@%s %s" % (alias, phrase)}
        ret = plug.stream(msg)
        self.assertEqual("%s: %s" % (", ".join(aliases), phrase),
                         ret)

    def test_stream_all(self):
        alias1 = 'foo'
        aliases1 = ['ola', 'cabron']
        alias2 = 'ini'
        aliases2 = ['mani', 'mo']
        phrase = 'tu va bien?'
        cPickle.dump({alias1: aliases1, alias2: aliases2}, self.temp_file)
        self.temp_file.close()

        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        msg = {'body': '@all %s' % (phrase)}
        ret = plug.stream(msg)
        self.assertEqual("%s: %s" % (", ".join(sorted(aliases1 + aliases2)),
                                     phrase), ret)

    def test_stream_no_msg_return(self):
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        ret = plug.stream({'body': ""})
        self.assertIsNone(ret)

    def test_stream_no_atmessage_return(self):
        plug = nonobot.plugins.groupalias.Plugin(FakeConfig(self.temp_file))
        ret = plug.stream({'body': "hola hola"})
        self.assertIsNone(ret)
