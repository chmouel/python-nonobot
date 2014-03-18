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


class Plugin(object):
    def __init__(self, config):
        pass

    def foo(self, msg, **kwargs):
        return "Hello World"

    def foo_multiple(self, msg, **kwargs):
        return ["Hello", "World"]

    def foo_doc(self, msg, **kwargs):
        "THIS IS SOME DOC"
        pass

    def stream(self, msg, **kwargs):
        if msg['body'] != 'callstream':
            return
        return "Hello Stream"