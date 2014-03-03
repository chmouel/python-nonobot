import re

bug_re = re.compile('.*bug (\d{4,})')

BASE_URL = 'https://bugs.launchpad.net/bugs'


class Plugin(object):
    def __init__(self, config):
        self.config = config

    def stream(self, line):
        match = bug_re.match(line)
        if match:
            return '{0}/{1}'.format(BASE_URL, match.group(1))
