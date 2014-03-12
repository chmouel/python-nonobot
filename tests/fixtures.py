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
import shutil
import tempfile


class FakeMessage(object):
    def __init__(self, message=None, nick=None):
        self.nick = nick
        self.message = message

    def get_mucnick(self):
        return self.nick


class FakeFrom(object):
    bare = 'thedude'


class cleaned_tempdir(object):
    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, *args):
        try:
            shutil.rmtree(self.path)
        except OSError as exc:
            if exc.errno != 2:
                raise
