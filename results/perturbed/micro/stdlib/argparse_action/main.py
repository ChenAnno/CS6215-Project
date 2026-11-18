import argparse

class qf5bc_0(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

parser = argparse.ArgumentParser()
parser.add_argument("--name", action=qf5bc_0)
parser.parse_args(["--name", "ann"])
