# -*- encoding: utf-8 -*-

import cPickle
import logging
import os

GROUPS_PICKLE = "data/groups.pickle"


def _arguments(optp):
    """Add options to the global parser.

    :param optp: optparse parser
    :return: optparse parser
    """
    optp.add_option('-g', '--group-file', help='Group aliases DB file.',
                    dest='group_file', default="data/groups.pickle")
    return optp


class Plugin(object):
    def __init__(self, config):
        # TODO(chmouel): Use config['group_file']
        self.group_file = GROUPS_PICKLE
        self._groups = {}
        self.config = config

        if os.path.exists(self.group_file):
            self._groups = cPickle.load(open(self.group_file, 'r'))

    def _save_group_file(self):
        cPickle.dump(self._groups, open(self.group_file, 'wb'))

    def alias(self, msg):
        """Define an alias."""
        logging.debug('alias, msg=' + msg)
        _msg = msg.split()
        alias = _msg[0]
        aliases = _msg[1:]
        self._groups[alias] = aliases
        self._save_group_file()
        return '%s has been set to %s' % (
            alias, " ".join(aliases))

    def delete(self, msg):
        """Delete an alias."""
        alias = msg.split()[0]
        del self._groups[alias]
        self._save_group_file()
        return "%s has been deleted" % alias

    def list(self, msg):
        """List all available groups."""
        for g in self._groups.keys():
            yield 'alias %s => %s' % (
                g, ", ".join(self._groups.get(g))
            )

    def add(self, msg):
        """Add a member to an existing alias."""
        _msg = msg.split()
        alias = _msg[0]
        aliases = _msg[1:]

        if alias in self._groups:
            self._groups[alias] = self._groups[alias] + aliases
            self._save_group_file()
            return "%s aliases has been add to %s" % (
                " ".join(aliases), alias)
        else:
            return 'group %s has not been defined yet use alias' % alias

    def stream(self, msg):
        _msg = msg.split()
        alias = _msg[0]
        group_name = alias.replace('@', '')
        body_msg = " ".join(_msg[1:])

        if not alias.startswith("@"):
            return

        if group_name == 'all':
            all = set([item for sublist in self._groups.values()
                       for item in sublist])
            return ", ".join(all) + ": " + body_msg

        if group_name in self._groups:
            return ", ".join(self._groups[group_name]) + ": " + body_msg
