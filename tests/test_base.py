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
import unittest

import mock

import fixtures
import nonobot.base
import nonobot.plugins

import tests.fixtures as fix
import tests.sample1


@mock.patch('nonobot.base.NoNoBot.add_event_handler', mock.Mock())
@mock.patch('sleekxmpp.ClientXMPP.__init__', mock.Mock())
class BaseTest(unittest.TestCase):
    def setUp(self):
        self.username = 'hello'
        self.password = 'moto'
        self.nick = 'nick'
        self.room = 'room'

    def _make_plugins(self):
        plugin_manager = fix.make_plugins(allplugins=(tests.sample1,))
        return plugin_manager.get_methods({'foo: bar'})

    def test_init(self):
        with mock.patch('sleekxmpp.ClientXMPP.__init__') as mocked:
            cls = nonobot.base.NoNoBot(
                self.username, self.password, self.room, self.nick)
            mocked.assert_called_with(cls, self.username, self.password)

    def test_message_return_if_no_plugins(self):
        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room, self.nick)
        msg = {'body': 'hello moto'}

        m = cls.groupchat_message(msg)
        self.assertIsNone(m)

    def test_message_direct(self):
        plugins = self._make_plugins()

        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room,
            self.nick,
            plugins=plugins)

        msg = fixtures.FakeMessage(body="havanagila")
        m = cls.message(msg)
        self.assertIsNone(m)

        reply_mock = mock.Mock()
        msg = fixtures.FakeMessage(body="foo", reply_mock=reply_mock)
        m = cls.message(msg)
        reply_mock.assert_called_once_with('Hello World')

        reply_mock = mock.Mock()
        msg = fixtures.FakeMessage(body="foo_multiple",
                                   reply_mock=reply_mock)
        m = cls.message(msg)
        reply_mock.assert_called_once_with('Hello\nWorld')

        reply_mock = mock.Mock()
        msg = fixtures.FakeMessage(body="help",
                                   reply_mock=reply_mock)
        m = cls.message(msg)
        reply_msg = '[sample1] foo_doc: THIS IS SOME DOC'
        reply_mock.assert_called_once_with(reply_msg)

    def test_message_stream_nothing_todo(self):
        plugins = self._make_plugins()

        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room,
            self.nick,
            plugins=plugins)
        msg = {'body': 'hello moto'}

        m = cls.groupchat_message(msg)
        self.assertIsNone(m)

    def test_undefined_action_return(self):
        plugins = self._make_plugins()

        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room,
            self.nick,
            plugins=plugins)
        msg = {'body': '%s: unknown' % (self.nick)}

        m = cls.groupchat_message(msg)
        self.assertIsNone(m)

    @mock.patch('sleekxmpp.ClientXMPP.send_message')
    def test_help(self, mocked):
        plugins = self._make_plugins()

        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room,
            self.nick,
            plugins=plugins)

        msg = {'body': self.nick + ': help',
               'from': fixtures.FakeFrom}

        cls.groupchat_message(msg)

        mbody = '[sample1] foo_doc: THIS IS SOME DOC'
        mocked.assert_called_with(mtype='groupchat',
                                  mbody=mbody,
                                  mto='thedude')

    @mock.patch('sleekxmpp.ClientXMPP.send_message')
    def test_command(self, mocked):
        plugins = self._make_plugins()

        cls = nonobot.base.NoNoBot(self.username, self.password,
                                   self.room, self.nick, plugins=plugins)

        msg = {'body': self.nick + ': foo',
               'from': fixtures.FakeFrom}

        cls.groupchat_message(msg)

        mocked.assert_called_with(mtype='groupchat',
                                  mbody='Hello World',
                                  mto='thedude')

    @mock.patch('sleekxmpp.ClientXMPP.send_message')
    def test_stream(self, mocked):
        plugins = self._make_plugins()

        cls = nonobot.base.NoNoBot(
            self.username, self.password, self.room,
            self.nick,
            plugins=plugins)

        msg = {'body': 'callstream',
               'from': fixtures.FakeFrom}

        cls.groupchat_message(msg)

        mocked.assert_called_with(mtype='groupchat',
                                  mbody='Hello Stream',
                                  mto='thedude')
