import collections

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
        body = msg['body']

        if body.startswith(self.nick + ":"):
            _line = body[len(self.nick) + 1:].split()
            action = _line[0]
            if action == 'help' and 'help' in self.plugins:
                reply_msg = self.plugins['help']
            else:
                for plugin in self.plugins:
                    if action in self.plugins[plugin]:
                        action_ = self.plugins[plugin][action]['action']
                        reply_msg = action_(" ".join(_line[1:]))

        for plugin in self.plugins:
            if 'stream' not in self.plugins[plugin]:
                continue

            stream = self.plugins[plugin]['stream']['action'](body)
            if stream is not None:
                reply_msg = stream

        if isinstance(reply_msg, collections.Iterable) or \
           type(reply_msg) is list:
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
