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
import optparse
import socket
import sys

import nonobot.base
import nonobot.plugins


def main(args=None):
    """Main loop

    :param args: system argument to give to optparse.
    :return: :raise: connect error
    """
    if args is None:
        args = sys.argv
    optp = optparse.OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)

    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)

    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")

    path = nonobot.plugins.__path__[0]
    nonobot.plugins.plugins_add_extra_options(path, optp)
    opts, args = optp.parse_args(args=args)
    plugins = nonobot.plugins.get_plugins_methods(path, opts)

    if not all([opts.jid, opts.nick,
                opts.room, opts.password]):
        optp.print_help()
        return 1

    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    xmpp = nonobot.base.NoNoBot(
        jid=opts.jid,
        password=opts.password,
        room=opts.room,
        nick=opts.nick,
        plugins=plugins)

    xmpp.register_plugin('xep_0030')  # Service Discovery
    xmpp.register_plugin('xep_0045')  # Multi-User Chat
    xmpp.register_plugin('xep_0199')  # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    try:
        xmpp.connect()
        xmpp.process(block=True)
    except socket.error:
        logging.error("Error while connecting")
        raise

if __name__ == "__main__":
    sys.exit(main())
