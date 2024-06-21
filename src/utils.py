import os
import yaml


def file_read(root, filename):
    with open(os.path.join(root, filename), 'r') as f:
        return f.read()


def yaml_read(root, filename):
    exec_yaml = file_read(root, filename)
    return yaml.load(exec_yaml, Loader=yaml.FullLoader)
