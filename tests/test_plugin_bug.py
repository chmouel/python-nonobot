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

import mock
import unittest

import nonobot.plugins.bug

try:
    import launchpadlib
except ImportError:
    launchpadlib = False


class FakeLaunchPadBug(object):
    def __init__(self, ret):
        self.ret = ret

    def bugs(self, bug):
        return self.ret()


class PluginBugTest(unittest.TestCase):
    def test_convert_without_launchpadlib(self):
        bug_number = "10000"
        plugin = nonobot.plugins.bug.Plugin({}, False)
        self.assertEqual(plugin.stream("bug " + bug_number),
                         "%s/%s" % (nonobot.plugins.bug.BASE_URL,
                                    bug_number))

    @unittest.skipIf(not launchpadlib, "launchpadlib is not installed")
    @mock.patch("launchpadlib.launchpad.Launchpad.login_anonymously")
    def test_convert_with_launchpadlib(self, mocked):
        class FakeBugSet():
            title = "Fake Bug"
            web_link = "http://launchpad/bug/1000"
        mocked.return_value = FakeLaunchPadBug(FakeBugSet)
        plugin = nonobot.plugins.bug.Plugin({}, True)
        self.assertEqual(plugin.stream("bug 10000"),
                         "[Bug 10000] Fake Bug - http://launchpad/bug/1000")

    @unittest.skipIf(not launchpadlib, "launchpadlib is not installed")
    @mock.patch("launchpadlib.launchpad.Launchpad.login_anonymously")
    def test_convert_with_launchpadlib_bug_no_here(self, mocked):
        def keyerror():
            raise KeyError
        mocked.return_value = FakeLaunchPadBug(keyerror)
        plugin = nonobot.plugins.bug.Plugin({}, True)
        self.assertEqual(plugin.stream("bug 10000"),
                         "There is no such bug '10000'")

    @unittest.skipIf(not launchpadlib, "launchpadlib is not installed")
    @mock.patch("launchpadlib.launchpad.Launchpad.login_anonymously")
    def test_convert_with_launchpadlib_bug_no_match(self, mocked):
        plugin = nonobot.plugins.bug.Plugin({}, True)
        self.assertIsNone(plugin.stream("foo bar"))


if __name__ == '__main__':
    unittest.main()
