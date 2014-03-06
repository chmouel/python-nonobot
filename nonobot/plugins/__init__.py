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
import imp
import inspect
import os


def get_all_plugin_modules(path):
    for dirname, _, filenames in os.walk(path):
        for f in filenames:
            if not f.endswith(".py") or f == '__init__.py':
                continue
            path_join = os.path.join(dirname, f)
            yield imp.load_source(f.replace('.py', ''), path_join)


def plugins_add_extra_options(path, optp):
    for imported in get_all_plugin_modules(path):
        attributes = inspect.getmembers(imported)
        for x in attributes:
            if x[0] == '_arguments':
                x[1](optp)


def get_plugins_methods(path, config):
    plugins = {}
    docs = []

    for imported in get_all_plugin_modules(path):
        plugin = imported.Plugin(config)
        attributes = inspect.getmembers(plugin,
                                        lambda a: inspect.isroutine(a))
        actions = {}
        for a in attributes:
            method_name = a[0]
            if not method_name.startswith('_'):
                action = a[1]
                doc = a[1].__doc__
                if method_name == 'stream':
                    docstr = "[%s] %s" % (imported.__name__, doc)
                else:
                    docstr = "[%s] %s: %s" % (imported.__name__,
                                              method_name, doc)
                if doc is not None:
                    docs.append(docstr)
                actions[method_name] = dict(action=action, doc=doc)
        plugins[plugin] = actions

    plugins['help'] = docs
    return plugins


class Base(object):
    def __init__(self, config):
        self.config = config
