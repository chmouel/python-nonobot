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
import logging
import threading

import sleekxmpp


class NoNoBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password,
                 room, nick,
                 plugins=None):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.room = room
        self.nick = nick

        self.current_pollers = []
        self.current_timers = []

        self.plugins = plugins

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.groupchat_message)
        self.add_event_handler("message", self.message)

    def start(self, event):
        self.get_roster()
        self.send_presence()

        for poll in self.plugins['pollers']:
            # TODO(chmou): this is ugly but that would do for now
            interval, method = poll(self)
            self.start_poller(interval, method)

        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        wait=True)

    def start_poller(self, interval, method, args=None, kwargs=None):
        args = args or {}
        kwargs = kwargs or {}

        try:
            self.current_pollers.append((method, args, kwargs))
            self.program_next_poll(interval, method, args, kwargs)
        except Exception:
            logging.traceback()

    def stop_poller(self, method, args=None, kwargs=None):
        args = args or {}
        kwargs = kwargs or {}
        logging.debug('Stop polling of %s with args %s and kwargs %s' %
                      (method, args, kwargs))
        self.current_pollers.remove((method, args, kwargs))

    def program_next_poll(self, interval, method, args, kwargs):
        t = threading.Timer(interval=interval,
                            function=self.poller,
                            kwargs={'interval': interval,
                                    'method': method, 'args':
                                    args, 'kwargs': kwargs})
        self.current_timers.append(t)  # save the timer to be able to kill it
        t.setName('Poller thread for %s' % type(method.__self__).__name__)
        t.setDaemon(True)  # so it is not locking on exit
        t.start()

    def poller(self, interval, method, args, kwargs):
        previous_timer = threading.current_thread()
        if previous_timer in self.current_timers:
            logging.debug('Previous timer found and removed')
            self.current_timers.remove(previous_timer)

        if (method, args, kwargs) in self.current_pollers:
            # noinspection PyBroadException
            try:
                method(*args, **kwargs)
            except Exception:
                logging.error('A poller crashed')
            self.program_next_poll(interval, method, args, kwargs)

    def message(self, msg):
        reply_msg = None
        _line = msg['body'].split()
        action = _line[0]
        new_msg = (msg)
        new_msg['body'] = " ".join(_line[1:])

        if action == 'help' and 'help' in self.plugins:
            reply_msg = self.plugins['help']
        else:
            for plugin in self.plugins:
                if action in self.plugins[plugin]:
                    action_ = self.plugins[plugin][action]['action']
                    reply_msg = action_(new_msg, direct=True)

        if type(reply_msg) is list:
            reply_msg = "\n".join(reply_msg)

        if reply_msg:
            msg.reply(reply_msg).send()

    def groupchat_message(self, msg):
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
                        reply_msg = action_(new_msg, direct=False)

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
