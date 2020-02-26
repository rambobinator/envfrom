from .tools import Plugin, register_plugin

@register_plugin
class Kube(Plugin):
    """ Mirror specified kubernetes ressource volume keys (decoded) """

    _arguments = [
        (["ressource"], {"help": "Kubernetes ressource type",
                         "choices": ["secrets", "ConfigMap"]}),
        (["name"], {"help": "Kubernetes ressource name"}),
        (["-n", "--namespace"], {"help": "Kubernetes namespace",
                                 "default": None})
    ]

    def __init__(self, ressource, name, namespace=None):
        from kubernetes import client, config

        self.ressource = ressource
        self.name = name
        self.namespace = namespace

        if namespace is None:
            try:
                self.namespace = config.list_kube_config_contexts()[1]["context"]["namespace"]
            except KeyError:
                pass

        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        super().__init__(self)

    def get_secrets(self):
        from base64 import b64decode

        data = self.v1.read_namespaced_secret(name=self.name,
                                              namespace=self.namespace)
        return {k.upper(): b64decode(v.encode()).decode() for k, v in data.data.items()}

    def get_config_map(self):
        data = self.v1.read_namespaced_config_map(name=self.name,
                                                  namespace=self.namespace)
        return data.data

    def process(self):
        ressource_funct_dict = {
            "secrets": self.get_secrets,
            "ConfigMap": self.get_config_map
        }
        return ressource_funct_dict[self.ressource]()


__all__ = ["Kube"]
