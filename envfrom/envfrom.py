from argparse import ArgumentParser
from os import environ, execve
from shutil import which


class Launcher:
    """Call child process with custom environment"""

    def __init__(self):
        self.parser = ArgumentParser(description=self.__doc__)
        self.subparsers = self.parser.add_subparsers(help="env source")
        self.parser.add_argument("child", help="child process")

    def __call__(self):
        args = self.parser.parse_args()
        child_args = args.__dict__.pop("child").split(' ')
        child = which(child_args[0]) or None
        plugin_class = args.__dict__.pop("cls")
        plugin = plugin_class(**args.__dict__)
        env = environ
        env.update(plugin.process())
        execve(child, child_args, env)


launcher = Launcher()


def run():
    launcher()


__all__ = ["launcher", "run"]
