from __future__ import print_function, division, absolute_import

from os import path, listdir, environ, system
from pdb import set_trace

import pandas as pd
import yaml

from taxplots.utils import ordered_load, ChDir

def _validate_plot_dir(directory):
    pass

def _get_plots():
    pass

def _get_plot_info(plot_dir):
    plot_files = listdir(plot_dir)
    if 'info.yml' in plot_files:
        info_file = path.join(plot_dir, 'info.yml')
        with open(info_file) as f:
            info = ordered_load(f.read())
            info['directory'] = plot_dir
            return info

def _run_plot(plot):
    with ChDir(plot.directory) as cwd:
        result = system(plot.build_cmd)
    return result == 0

def list_plots():
    plot_dir = path.abspath(path.join(path.split(__file__)[0], '../contrib'))

    if not path.exists(plot_dir):
        raise IOError("Can't find plot directory: {0}".format(plot_dir))

    plots = [path.join(plot_dir, d) for d in listdir(plot_dir)]
    infos = [_get_plot_info(p) for p in plots]
    df = pd.DataFrame(infos)
    return df

def build_plots():
    print('building plots...')
    plots_df = list_plots()
    plots_df['build_successful'] = plots_df.apply(_run_plot, axis=1)

    # log successful builds
    success_df = plots_df[plots_df['build_successful'] == True]
    if not success_df.empty:
        print('\n\nSuccessfully Built:')
        print('-------------------')
        print(success_df[['plot_name','plot_id','build_cmd']])
        print('\n\n')

    # log error builds
    error_df = plots_df[plots_df['build_successful'] == False]
    if not error_df.empty:
        print('\n\nErrors while Building:')
        print('----------------------')
        print(error_df[['plot_name','plot_id','build_cmd']])
        print('\n\n')

def upload_plots():
    print('uploading plots...')
    access_key = environ.get('AWS_ACCESS_KEY')
    secret_key = environ.get('')
    upload_bucket = environ.get('')

    env_msg = 'Environment varibles not set {0}, try: export {0}=<some value>'

    if not access_key:
        raise ValueError(env_msg.format('AWS_ACCESS_KEY'))
    if not secret_key:
        raise ValueError(env_msg.format('AWS_SECRET_KEY'))
    if not upload_bucket:
        raise ValueError(env_msg.format('TAXPLOT_S3_BUCKET'))

