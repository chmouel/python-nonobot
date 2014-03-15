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
import inspect

import stevedore


class Manager(object):
    def __init__(self, extension_manager=None):
        self.extension_manager = extension_manager
        if self.extension_manager is None:
            self.extension_manager = self._extension_manager()

    def _extension_manager(self):
        manager = stevedore.extension.ExtensionManager(
            namespace='nonobot.plugins')
        return manager

    def add_extra_options(self, optp):
        for imported in self.extension_manager:
            attributes = inspect.getmembers(imported.plugin)
            for x in attributes:
                if x[0] == '_arguments':
                    x[1](optp)

    def get_methods(self, config):
        plugins = {}
        docs = []
        for imported in self.extension_manager:
            plugin = imported.plugin.Plugin(config)
            attributes = inspect.getmembers(plugin,
                                            lambda a: inspect.isroutine(a))
            actions = {}
            for a in attributes:
                method_name = a[0]
                if not method_name.startswith('_'):
                    action = a[1]
                    doc = a[1].__doc__
                    bname = imported.plugin.__name__.split('.')[-1]
                    if method_name == 'stream':
                        docstr = "[%s] %s" % (bname, doc)
                    else:
                        docstr = "[%s] %s: %s" % (bname, method_name, doc)
                    if doc is not None:
                        docs.append(docstr)
                    actions[method_name] = dict(action=action, doc=doc)
            plugins[plugin] = actions

        plugins['help'] = docs
        return plugins


class Base(object):
    def __init__(self, config):
        self.config = config
