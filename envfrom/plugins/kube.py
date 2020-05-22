from os import listdir
from os.path import isdir, isfile, realpath

import yaml
from nested_lookup import nested_lookup

from .tools import Plugin, register_plugin


def get_yaml_documents(path, documents=None):
    if documents is None:
        documents = []
    if isfile(path) and path.endswith((".yaml", ".yml")):
        with open(path, newline=None) as f:
            documents.extend(yaml.safe_load_all(f))
    if isdir(path):
        for e in listdir(path):
            get_yaml_documents(path + "/" + e, documents)
    return documents


@register_plugin
class Kube(Plugin):
    """ Mirror specified kubernetes ressource volume keys (decoded) """

    _arguments = [
        (["ressource"], {"help": "Kubernetes ressource type",
                         "choices": ["secrets", "ConfigMap", "manifest"]}),
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

        self.ressource_funct_dict = {
            "secrets": self.get_secrets,
            "ConfigMap": self.get_config_map,
            "manifest": self.get_manifests
        }

        super().__init__(self)

    def get_secrets(self, name=None):
        from base64 import b64decode

        data = self.v1.read_namespaced_secret(name=name or self.name,
                                              namespace=self.namespace)
        return {k.upper(): b64decode(v.encode()).decode() for k, v in data.data.items()}

    def get_config_map(self, name=None):
        data = self.v1.read_namespaced_config_map(name=name or self.name,
                                                  namespace=self.namespace)
        return data.data

    def get_manifest_data(self, doc):
        for match in nested_lookup("data", doc):
            self.env_dict.update(match)

    def get_manifest_env(self, doc):
        for match in nested_lookup("env", doc):
            for m in match:
                try:
                    self.env_dict[m["name"]] = m["value"]
                except KeyError:
                    pass

    def get_manifest_envfrom(self, doc, resource, resource_key):
        for match in nested_lookup(resource_key, doc):
            try:
                data = self.ressource_funct_dict[resource](match["name"])
                self.env_dict.update(data)
            except KeyError:
                pass

    def get_manifest_valuefrom(self, doc, resource, resource_key):
        for match in nested_lookup(resource_key, doc):
            try:
                data = self.ressource_funct_dict[resource](match["name"])
                self.env_dict[match["key"]] = data[match["key"]]
            except KeyError:
                pass

    def get_manifests(self):
        self.env_dict = {}
        for doc in get_yaml_documents(realpath(self.name)):
            self.get_manifest_data(doc)
            self.get_manifest_env(doc)
            self.get_manifest_envfrom(doc, "ConfigMap", "configMapRef")
            self.get_manifest_envfrom(doc, "secrets", "secretRef")
            self.get_manifest_valuefrom(doc, "ConfigMap", "configMapKeyRef")
            self.get_manifest_valuefrom(doc, "secrets", "secretKeyRef")
        return self.env_dict

    def process(self):
        return self.ressource_funct_dict[self.ressource]()


__all__ = ["Kube"]
