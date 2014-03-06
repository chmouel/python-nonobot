try:
    from launchpadlib import launchpad
except ImportError:
    launchpad = False

import re
import tempfile

import nonobot.plugins

bug_re = re.compile('.*bug (\d{4,})')

BASE_URL = 'https://bugs.launchpad.net/bugs'


class Plugin(nonobot.plugins.Base):
    def __init__(self, config):
        if launchpad:
            self.lp = launchpad.Launchpad.login_anonymously(
                'nonobotgrab', 'production', tempfile.gettempdir())

    def stream(self, line):
        """parse 'bug number' and expand it to launchpad bug url."""
        match = bug_re.match(line)
        if not match:
            return
        if launchpad:
            try:
                # TODO(chmouel): chaching
                lpbug = self.lp.bugs(int(match.group(1)))
            except(KeyError):
                return "There is no such bug '%s'" % match.group(1)
            if lpbug:
                return "[Bug %s] %s - %s" % (match.group(1),
                                             lpbug.title,
                                             lpbug.web_link)
        else:
            return '{0}/{1}'.format(BASE_URL, match.group(1))
