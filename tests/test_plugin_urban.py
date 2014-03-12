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

import json
import random
import unittest

import httpretty
import mock

import nonobot.plugins.urban

URBAN_REPLY_ONE = {'list': [{'word': 'foo',
                             'example': 'foo is cool',
                             'permalink': 'http://foobar.urbanup.com/123',
                             'definition': 'The master of foo'}]}

URBAN_REPLY_MULTIPLE = {'list': [URBAN_REPLY_ONE['list'][0],
                                 {'word': 'foo',
                                  'example': 'bar is cooler',
                                  'permalink': 'http://foobar.urbanup.com/123',
                                  'definition': 'Bar is like drinking party'}]}

URBAN_REPLY_NOTHING = {'list': []}


class UrbanTest(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

    def test_good(self):
        plugin = nonobot.plugins.urban.Plugin({})
        term = {'body': 'foo'}
        url = '%s/define?term=%s' % (nonobot.plugins.urban.BASE_URL, term)

        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(URBAN_REPLY_ONE),
                               content_type="application/json")

        reply = '[1/1]  %(definition)s example: %(example)s / ' \
                '%(permalink)s' % URBAN_REPLY_ONE['list'][0]

        self.assertEqual(plugin.urban(term), reply)

    def test_multiple_with_index(self):
        plugin = nonobot.plugins.urban.Plugin({})
        term = {'body': 'foo 2'}
        url = '%s/define?term=%s' % (nonobot.plugins.urban.BASE_URL, term)

        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(URBAN_REPLY_MULTIPLE),
                               content_type="application/json")

        reply = '[2/2]  %(definition)s example: %(example)s / ' \
                '%(permalink)s' % URBAN_REPLY_MULTIPLE['list'][1]

        self.assertEqual(plugin.urban(term), reply)

    def test_excessive_index(self):
        plugin = nonobot.plugins.urban.Plugin({})
        term = {'body': 'foo 5'}
        url = '%s/define?term=%s' % (nonobot.plugins.urban.BASE_URL, term)

        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(URBAN_REPLY_ONE),
                               content_type="application/json")

        reply = 'That\'s way too much we have only 1 items'
        self.assertEqual(plugin.urban(term), reply)

    def test_nothing(self):
        plugin = nonobot.plugins.urban.Plugin({})
        term = {'body': 'nothing'}
        url = '%s/define?term=%s' % (nonobot.plugins.urban.BASE_URL, term)

        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(URBAN_REPLY_NOTHING),
                               content_type="application/json")

        reply = 'Don\'t make up crap please. That thing don\'t even exist ' \
                'in the urban dictionary'

        self.assertEqual(plugin.urban(term), reply)

    def test_random(self):
        plugin = nonobot.plugins.urban.Plugin({})
        url = '%s/random' % nonobot.plugins.urban.BASE_URL
        rnd = random.randint(0, 1)

        with mock.patch("random.randint", return_value=rnd):
            httpretty.register_uri(httpretty.GET, url,
                                   body=json.dumps(URBAN_REPLY_MULTIPLE),
                                   content_type="application/json")

            reply = '[%(word)s] %(definition)s example: %(example)s / ' \
                    '%(permalink)s' % URBAN_REPLY_MULTIPLE['list'][rnd]

            self.assertEqual(plugin.urban({'body': ''}), reply)
