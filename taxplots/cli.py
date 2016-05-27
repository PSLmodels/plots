from __future__ import print_function, division, absolute_import
from os import path, listdir, environ

def _validate_plot_dir(directory):
    pass

def _get_plots():
    pass

def list_plots():
    plots = path.join(path.split(__file__)[0], '../contrib')
    print(plots)
    return plots

def build_plots():
    print('building plots...')
    pass

def upload_plots():
    print('uploading plots...')
    access_key = environ.get('')
    secret_key = environ.get('')
