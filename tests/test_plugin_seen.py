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
import datetime
import unittest
import urllib

import mock

import nonobot.plugins.seen

import fixtures


class PluginTest(unittest.TestCase):
    def test_seen_stream_record(self):
        dt = datetime.datetime.now()
        user = 'unamigo'
        with mock.patch('datetime.datetime') as mocked:
            mocked.now.return_value = dt
            plugin = nonobot.plugins.seen.Plugin({})
            msg = fixtures.FakeMessage(nick=user)
            plugin.stream(msg)
            self.assertIn(user, plugin.seen_dict)
            self.assertEqual(plugin.seen_dict[user], dt)

    def test_seen(self):
        user = 'eltorreador'
        dt = datetime.datetime.now()
        plugin = nonobot.plugins.seen.Plugin({})
        plugin.seen_dict = {user: dt}
        msg = {'body': user}

        ret = plugin.seen(msg)
        self.assertTrue(ret.startswith("I saw %s" % user))
        self.assertTrue(ret.endswith("just now"))

    def test_seen_with_space(self):
        user = 'eltorreador del campo'
        dt = datetime.datetime.now()
        plugin = nonobot.plugins.seen.Plugin({})
        plugin.seen_dict = {urllib.quote(user): dt}
        msg = {'body': user}

        ret = plugin.seen(msg)
        self.assertTrue(ret.startswith("I saw %s" % user))
        self.assertTrue(ret.endswith("just now"))

    def test_seen_with_accents(self):
        user = 'El Niño dél pampa'
        dt = datetime.datetime.now()
        plugin = nonobot.plugins.seen.Plugin({})
        plugin.seen_dict = {urllib.quote(user): dt}
        msg = {'body': user}

        ret = plugin.seen(msg)
        self.assertTrue(ret.startswith("I saw %s" % user))
        self.assertTrue(ret.endswith("just now"))
