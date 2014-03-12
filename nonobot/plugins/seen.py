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

import nonobot.plugins
import nonobot.utils as nutils


class Plugin(nonobot.plugins.Base):

    def __init__(self, config):
        self.seen_dict = {}

    def seen(self, msg, **kwargs):
        """ask the bot when last a user was seen here."""
        ret = []
        for nick in msg['body'].split(" "):
            cleaned = nutils.clean_nick(nick)
            if cleaned in self.seen_dict:
                pretty = nutils.pretty_date(self.seen_dict[cleaned])
                ret.append("I saw %s %s" % (cleaned, pretty))
        return ret

    def stream(self, msg):
        nick = msg.get_mucnick()
        self.seen_dict[nutils.clean_nick(nick)] = datetime.datetime.now()
