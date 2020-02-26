from envfrom.envfrom import launcher


class Plugin:
    """ Abstract Class"""

    _arguments = None

    def __init__(self, *args, **kwargs):
        if self._arguments is None:
            raise NotImplementedError

    def process(self):
        """ Return environment as a dict"""
        raise NotImplementedError


def register_plugin(cls):
    plugin_parser = launcher.subparsers.add_parser(cls.__name__.lower(),
                                                   help=cls.__doc__)
    plugin_parser.set_defaults(cls=cls)
    for argument in cls._arguments:
        args, kwargs = argument
        plugin_parser.add_argument(*args, **kwargs)
    return cls


__all__ = ["Plugin", "register_plugin"]
