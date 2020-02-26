from .tools import Plugin, register_plugin

# Made for testing purpose
@register_plugin
class CLI(Plugin):
    """ Dict values: FOO=BAR BAR=FOO """

    _arguments = [
        (["-l", "--list"], {"dest": "env_list",
                            "nargs": '*',
                            "help": "Dict values"})
    ]

    def __init__(self, env_list):
        self.env_list = env_list or []
        super().__init__(self)

    def process(self):
        env_dict = {}
        for env in self.env_list:
            try:
                k, v = env.split('=')
                env_dict[k] = v
            except ValueError:
                pass
        return env_dict


__all__ = ["CLI"]
