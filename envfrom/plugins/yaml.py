from os import listdir
from os.path import isdir, isfile, realpath

import yaml
from nested_lookup import nested_lookup

from .kube import Kube
from .tools import Plugin, register_plugin


def get_documents(path, documents=None):
    if documents is None:
        documents = []
    if isfile(path):
        with open(path, newline=None) as f:
            documents.extend(yaml.safe_load_all(f))
    if isdir(path):
        for e in listdir(path):
            get_documents(path + "/" + e, documents)
    return documents


@register_plugin
class Yaml(Plugin):
    """ Parse manifests to replicate the env of your app """

    _arguments = [
        (["path"], {"help": "manifest(s) location, can be a directory"})
    ]

    def __init__(self, path):
        self.docs = get_documents(realpath(path))
        self.env_dict = {}
        super().__init__(self)

    def get_data(self, doc):
        for match in nested_lookup("data", doc):
            self.env_dict.update(match)

    def get_env(self, doc):
        for match in nested_lookup("env", doc):
            for m in match:
                try:
                    self.env_dict[m["name"]] = m["value"]
                except KeyError:
                    pass

    def get_envfrom(self, doc, resource, resource_key):
        for match in nested_lookup(resource_key, doc):
            try:
                data = Kube(resource, match["name"]).process()
                self.env_dict.update(data)
            except KeyError:
                pass

    def get_valuefrom(self, doc, resource, resource_key):
        for match in nested_lookup(resource_key, doc):
            try:
                data = Kube(resource, match["name"]).process()
                self.env_dict[match["key"]] = data[match["key"]]
            except KeyError:
                pass

    def process(self):
        for doc in self.docs:
            self.get_data(doc)
            self.get_env(doc)
            self.get_envfrom(doc, "ConfigMap", "configMapRef")
            self.get_envfrom(doc, "secrets", "secretRef")
            self.get_valuefrom(doc, "ConfigMap", "configMapKeyRef")
            self.get_valuefrom(doc, "secrets", "secretKeyRef")
        return self.env_dict


__all__ = ["Yaml"]
