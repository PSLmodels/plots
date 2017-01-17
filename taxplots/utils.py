import os
import yaml

from os import path
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader

def render_template(template, template_args, output_file):

    # register names for known templates
    templates = dict(responsive='templates/responsive_flexbox.j2')
    here = path.dirname(path.abspath(__file__))

    if os.path.exists(template):
        template_path = template
    elif template in list(templates.keys()):
        template_path = templates.get(template)
    else:
        template_path = path.join(here, 'templates', template)

    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template(template_path).render(**template_args)
    with open(output_file, 'w') as f:
        f.write(content)

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

class DirectoryContext(object):
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
