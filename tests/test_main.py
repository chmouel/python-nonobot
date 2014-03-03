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
import socket
import unittest

import nonobot.main


class MainTest(unittest.TestCase):
    @mock.patch('nonobot.plugins.plugins_add_extra_options', mock.Mock())
    @mock.patch('optparse.OptionParser.print_help', mock.Mock())
    def test_at_least_options(self):
        args = ['test',
                '-j', 'jid@jid.com',
                '-p', 'password',
                '-r', 'room@conference.jid.com']
        self.assertEqual(nonobot.main.main(args), 1)
        args = ['test',
                '-j', 'jid@jid.com',
                '-p', 'password',
                '-n', 'nick']
        self.assertEqual(nonobot.main.main(args), 1)
        args = ['test',
                '-j', 'jid@jid.com',
                '-r', 'room@conference.jid.com',
                '-n', 'nick']
        self.assertEqual(nonobot.main.main(args), 1)
        args = ['test',
                '-p', 'password',
                '-r', 'room@conference.jid.com',
                '-n', 'nick']
        self.assertEqual(nonobot.main.main(args), 1)

    @mock.patch('nonobot.plugins.get_all_plugin_modules', mock.MagicMock())
    @mock.patch('nonobot.base.NoNoBot')
    def test_all_running_options(self, mock):
        jid = 'jid@jid.com'
        room = 'room@conference.jid.com'
        password = 'password'
        nick = 'nick'

        args = ['test',
                '-j', jid,
                '-p', password,
                '-r', room,
                '-n', nick]

        self.assertIsNone(nonobot.main.main(args))

        mock.assert_called_once_with(
            jid=jid,
            room=room,
            password=password,
            nick=nick,
            plugins={}
        )

    @mock.patch('nonobot.base.NoNoBot.connect', side_effect=socket.error)
    def test_all_error_connect_pass(self, mocked):
        jid = 'jid@jid.com'
        room = 'room@conference.jid.com'
        password = 'password'
        nick = 'nick'

        args = ['test',
                '-j', jid,
                '-p', password,
                '-r', room,
                '-n', nick]

        self.assertRaises(socket.error, nonobot.main.main, args)

if __name__ == '__main__':
    unittest.main()
