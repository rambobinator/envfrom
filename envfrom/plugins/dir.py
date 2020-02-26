from os import listdir
from os.path import basename, isdir, isfile, realpath

from .tools import Plugin, register_plugin


# rm_ass: Standard envdir doesn't perform recursion
def get_envdir(path, env=None):
    if env is None:
        env = {}
    if isfile(path):
        with open(path, newline=None) as f:
            env[basename(path)] = f.read()[:-1]
    if isdir(path):
        for e in listdir(path):
            get_envdir(path + "/" + e, env)
    return env


@register_plugin
class Dir(Plugin):
    """ Set environment according to files in a specified path """

    _arguments = [
        (["path"], {"help": "envdir path"})
    ]

    def __init__(self, path):
        self.path = path
        super().__init__(self)

    def process(self):
        return get_envdir(realpath(self.path))


__all__ = ["Dir"]
