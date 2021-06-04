import os

import hvac

from .tools import Plugin, register_plugin


@register_plugin
class Vault(Plugin):
    """Fetch secrets from Vault paths"""

    _arguments = [
        (["path"], {"help": ("Path of the secret to fetch from the Vault"
                             "servers. Multiple paths can be specified."),
                    "nargs": "*"}),
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

        if "KUBERNETES_PORT" in os.environ:
            f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')
            jwt = f.read()
            self.client.auth_kubernetes("default", jwt)

        self.engine = self.client.secrets.kv.v2
        super().__init__(self)

    def get_secret(self, path):
        key = None
        if "#" in path:
            path, key = path.split("#", 1)

        mount_point, path = path.split("/", 1)
        response = self.engine.read_secret_version(mount_point=mount_point,
                                                   path=path)

        data = response["data"]["data"]
        if key:
            return data[key]
        return data

    def process(self):
        env = {}

        for key, value in os.environ.items():
            if value.startswith("vault:"):
                env[key] = self.get_secret(value[6:])

        for path in self.paths:
            secret = self.get_secret(path)
            if isinstance(secret, dict):
                for key, value in secret.items():
                    env[key.upper()] = value
            else:
                env[key.upper()] = secret
        return env


__all__ = ["Vault"]
