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

import mock
import unittest

import fixtures
import nonobot.base
import nonobot.plugins

SAMPLE_PLUGIN_METHOD = """
class Plugin:
    def __init__(self, config):
        pass
    def foo(self, msg):
        return "Hello World"
    def foo_doc(self, msg):
        "THIS IS SOME DOC"
        pass
"""

SAMPLE_PLUGIN_STREAM = """
class Plugin:
    def __init__(self, config):
        pass

    def stream(self, msg):
        return "Hello Stream"
"""


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.username = 'hello'
        self.password = 'moto'
        self.nick = 'nick'
        self.room = 'room'

    @mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.__init__')
    def test_init(self, mocked):
        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room, self.nick)
        mocked.assert_called_with(cls, self.username, self.password)

    @mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.__init__', mock.Mock())
    def test_message_return_if_no_plugins(self):
        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room, self.nick)
        msg = {'body': 'hello moto'}

        m = cls.message(msg)
        self.assertIsNone(m)

    @mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.__init__', mock.Mock())
    def test_message_stream_nothing_todo(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/tstream.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_METHOD)
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            cls = nonobot.base.NoNoBot(
                self.username, self.password, self.room,
                self.nick,
                plugins=plugins)
            msg = {'body': 'hello moto'}

            m = cls.message(msg)
            self.assertIsNone(m)

    @mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.__init__', mock.Mock())
    def test_undefined_action_return(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/tstream.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_METHOD)
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            cls = nonobot.base.NoNoBot(
                self.username, self.password, self.room,
                self.nick,
                plugins=plugins)
            msg = {'body': '%s: unknown' % (self.nick)}

            m = cls.message(msg)
            self.assertIsNone(m)

    @mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.__init__', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.send_message')
    def test_help(self, mocked):
        with fixtures.cleaned_tempdir() as path:
            class From(object):
                bare = 'thedude'
            test_file = path + "/testhelp.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_METHOD)
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            cls = nonobot.base.NoNoBot(
                self.username, self.password, self.room,
                self.nick,
                plugins=plugins)

            msg = {'body': self.nick + ': help',
                   'from': fixtures.FakeFrom}

            cls.message(msg)

            mbody = '[testhelp] foo_doc: THIS IS SOME DOC'
            mocked.assert_called_with(mtype='groupchat',
                                      mbody=mbody,
                                      mto='thedude')

    @mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.__init__', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.send_message')
    def test_command(self, mocked):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/testcommand.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_METHOD)
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            cls = nonobot.base.NoNoBot(self.username, self.password,
                                       self.room, self.nick, plugins=plugins)

            msg = {'body': self.nick + ': foo',
                   'from': fixtures.FakeFrom}

            cls.message(msg)

            mocked.assert_called_with(mtype='groupchat',
                                      mbody='Hello World',
                                      mto='thedude')

    @mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.__init__', mock.Mock())
    @mock.patch('sleekxmpp.ClientXMPP.send_message')
    def test_stream(self, mocked):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/teststream.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_STREAM)
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            cls = nonobot.base.NoNoBot(
                self.username, self.password, self.room,
                self.nick,
                plugins=plugins)

            msg = {'body': 'callstream',
                   'from': fixtures.FakeFrom}

            cls.message(msg)

            mocked.assert_called_with(mtype='groupchat',
                                      mbody='Hello Stream',
                                      mto='thedude')
