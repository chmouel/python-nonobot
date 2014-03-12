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
import cPickle
import logging
import os

import nonobot.plugins

GROUPS_PICKLE = "data/groups.pickle"


def _arguments(optp):
    """Add options to the global parser.

    :param optp: optparse parser
    :return: optparse parser
    """
    optp.add_option('-g', '--group-file', help='Group aliases DB file.',
                    dest='group_file', default="data/groups.pickle")
    return optp


class Plugin(nonobot.plugins.Base):
    def __init__(self, config):
        if config.group_file:
            self.group_file = config.group_file
        else:
            self.group_file = GROUPS_PICKLE

        self._groups = {}
        self.config = config

        if os.path.exists(self.group_file):
            try:
                self._groups = cPickle.load(open(self.group_file, 'r'))
            except(EOFError):
                self._groups = {}

    def _save_group_file(self):
        cPickle.dump(self._groups, open(self.group_file, 'wb'))

    def alias(self, msg):
        """define a group."""
        logging.debug('alias, msg=' + msg['body'])
        _msg = msg['body'].split()
        if not _msg:
            return
        alias = _msg[0]
        aliases = _msg[1:]
        self._groups[alias] = aliases
        self._save_group_file()
        return '%s has been set to %s' % (
            alias, " ".join(aliases))

    def delete(self, msg):
        """delete a group."""
        alias = msg['body'].split()[0]
        del self._groups[alias]
        self._save_group_file()
        return "%s has been deleted" % alias

    def list(self, msg):
        """list all available groups."""
        ret = []
        for g in self._groups.keys():
            ret.append('alias %s => %s' % (
                g, ", ".join(self._groups.get(g))
            ))
        return ret

    def add(self, msg):
        """add a member to an existing group."""
        _msg = msg['body'].split()
        alias = _msg[0]
        aliases = _msg[1:]

        if alias in self._groups:
            self._groups[alias] = self._groups[alias] + aliases
            self._save_group_file()
            return "%s aliases has been added to %s" % (
                " ".join(aliases), alias)
        else:
            return 'group %s has not been defined yet use alias' % alias

    def stream(self, msg):
        """@group will message to all the group members."""
        _msg = msg['body'].strip().split()
        if not _msg:
            return
        alias = _msg[0]
        group_name = alias.replace('@', '')
        body_msg = " ".join(_msg[1:])

        if not alias.startswith("@"):
            return

        if group_name == 'all':
            all = sorted(set([item for sublist in self._groups.values()
                              for item in sublist]))
            return ", ".join(all) + ": " + body_msg

        if group_name in self._groups:
            return ", ".join(self._groups[group_name]) + ": " + body_msg
