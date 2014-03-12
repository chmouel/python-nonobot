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
import sleekxmpp


class NoNoBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password,
                 room, nick,
                 plugins=None):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.room = room
        self.nick = nick

        self.plugins = plugins

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.message)

    def start(self, event):
        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        wait=True)

    def message(self, msg):
        reply_msg = None

        if not self.plugins:
            return

        if msg['body'].startswith(self.nick + ":"):
            _line = msg['body'][len(self.nick) + 1:].split()
            action = _line[0]
            new_msg = (msg)
            new_msg['body'] = " ".join(_line[1:])

            if action == 'help' and 'help' in self.plugins:
                reply_msg = self.plugins['help']
            else:
                for plugin in self.plugins:
                    if action in self.plugins[plugin]:
                        action_ = self.plugins[plugin][action]['action']
                        reply_msg = action_(new_msg)

        for plugin in self.plugins:
            if 'stream' not in self.plugins[plugin]:
                continue

            stream = self.plugins[plugin]['stream']['action'](msg)
            if stream is not None:
                reply_msg = stream

        if type(reply_msg) is list:
            for g in reply_msg:
                self.send_message(
                    mbody=g,
                    mto=msg['from'].bare,
                    mtype='groupchat')
        elif reply_msg:
            self.send_message(
                mbody=reply_msg,
                mto=msg['from'].bare,
                mtype='groupchat')
