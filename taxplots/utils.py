import os
import yaml
from collections import OrderedDict

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

class ChDir(object):
    """
    Context Manager for changing directories
    """
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path
 
    def __enter__(self):
        os.chdir(self.new_dir)
 
    def __exit__(self, *args):
        os.chdir(self.old_dir)
