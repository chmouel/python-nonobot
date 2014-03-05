# coding=utf-8
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

    for imported in get_all_plugin_modules(path):
        plugin = imported.Plugin(config)
        attributes = inspect.getmembers(plugin,
                                        lambda a: inspect.isroutine(a))
        actions = {}
        for a in attributes:
            method_name = a[0]
            if not method_name.startswith('_'):
                # TODO(chmouel): Build help command
                actions[method_name] = dict(action=a[1], doc=a[1].__doc__)

        plugins[plugin] = actions
    return plugins


class Base(object):
    def __init__(self, config):
        self.config = config
