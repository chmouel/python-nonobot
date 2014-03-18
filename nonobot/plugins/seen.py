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
import random
import urllib

import nonobot.plugins
import nonobot.utils as nutils

RANDOM_TALK = ["talking", "pipoting", "spreching", "hablaning", "parlaring"]
NOIP = "I ain't seen no one, I promess mister sherriffman."


class Plugin(nonobot.plugins.Base):

    def __init__(self, config):
        self.config = config
        self.seen_dict = {}

    def list_seen(self, msg, **kwargs):
        """List all users that has been seen by nonobot."""
        ret = []
        msg = {}

        for u in self.seen_dict:
            msg['body'] = u
            ret.append(self.seen(msg, here="on " + self.config.room))
        if not ret:
            ret.append(NOIP)
        return ret

    def seen(self, msg, here="here", **kwargs):
        """ask the bot when last a user was seen here."""
        cleaned = nutils.clean_nick(msg['body'])
        if cleaned in self.seen_dict:
            unquoted = urllib.unquote(cleaned)
            pretty = nutils.pretty_date(self.seen_dict[cleaned])
            return "I saw %s %s %s %s" % (unquoted,
                                          random.choice(RANDOM_TALK),
                                          here,
                                          pretty)
        else:
            return NOIP

    def stream(self, msg, **kwargs):
        nick = msg.get_mucnick()
        self.seen_dict[nutils.clean_nick(nick)] = datetime.datetime.now()
