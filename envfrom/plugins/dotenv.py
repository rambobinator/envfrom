from os.path import realpath

from .tools import Plugin, register_plugin


def get_dotenv(path):
    env_dict = {}
    with open(path, newline=None) as f:
        for l in f:
            if l.startswith('#'):
                continue
            try:
                i = l[:-1].index('=')
                env_dict.update({l[:i]: l[(i + 1):-1]})
            except ValueError:
                pass
    return env_dict


@register_plugin
class Dotenv(Plugin):
    """ Set environment according to .env file """

    _arguments = [
        (["path"], {"help": ".env file"})
    ]

    def __init__(self, path):
        self.path = path
        super().__init__(self)

    def process(self):
        return get_dotenv(realpath(self.path))


__all__ = ["Dotenv"]
