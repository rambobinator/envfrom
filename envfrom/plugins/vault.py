import os

import hvac

from .tools import Plugin, register_plugin


@register_plugin
class Vault(Plugin):
    """Fetch secrets from Vault paths"""

    _arguments = [
        (["path"], {"help": ("Path of the secret to fetch from the Vault"
                             "servers. Multiple paths can be specified."),
                    "nargs": "+"}),
        (["--addr"], {"help": ("Address of the Vault server. The default is "
                               "https://127.0.0.1:8200. This can also be "
                               "specified via the VAULT_ADDR environment "
                               "variable."), "default": None})
    ]

    def __init__(self, path, addr=None):
        self.paths = path
        if addr is None:
            addr = os.environ.get("VAULT_ADDR", "https://127.0.0.1:8200")
        self.client = hvac.Client(url=addr)
        self.engine = self.client.secrets.kv.v2
        super().__init__(self)

    def process(self):
        env = {}
        for path in self.paths:
            mount_point, path = path.split("/", 1)
            response = self.engine.read_secret_version(mount_point=mount_point,
                                                       path=path)
            for key, value in response["data"]["data"].items():
                env[key.upper()] = value
        return env


__all__ = ["Vault"]
