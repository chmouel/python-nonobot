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
import nonobot.plugins


class Plugin(nonobot.plugins.Base):
    parent_class = None
    intervals = 3

    def send_message(self, msg):
        self.parent_class.send_message(
            mbody=msg,
            mto=self.parent_class.room,
            mtype='groupchat')

    def _refresh_gerrit(self):
        pass

    def _init_poll(self, parent_class):
        self.parent_class = parent_class
        return (self.intervals, self._refresh_gerrit)
