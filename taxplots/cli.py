from __future__ import print_function, division, absolute_import

from functools import partial
from os import path, listdir, environ, system, walk
from pdb import set_trace

import pandas as pd

import boto3
import botocore

from taxplots.utils import ordered_load, DirectoryContext

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

    with DirectoryContext(plot.directory) as dir_ctx:
        result = system(plot.build_cmd)

    return result == 0

def _upload_plot(client, bucket, plot):

    extra_args = dict(ACL='public-read')
    url_template = 'https://s3.amazonaws.com/{0}/{1}'

    with DirectoryContext(plot.directory) as dir_ctx:
        try:
            resp = client.upload_file(plot.content, bucket,
                                      path.join(plot.plot_id, plot.content),
                                      ExtraArgs=extra_args)

            if path.exists('resources'):
                for dir_path, subdir_list, file_list in walk('resources'):
                    for fname in file_list:
                        full_path = path.join(dir_path, fname)
                        client.upload_file(full_path, bucket,
                                           path.join(plot.plot_id, full_path),
                                           ExtraArgs=extra_args)
            return url_template.format(bucket, plot.content)

        except botocore.exceptions.ClientError as e:
            print(e.response)
            return False


def list_plots():
    plot_dir = path.abspath(path.join(path.split(__file__)[0], '../contrib'))

    if not path.exists(plot_dir):
        raise IOError("Can't find plot directory: {0}".format(plot_dir))

    plots = [path.join(plot_dir, d) for d in listdir(plot_dir)]
    infos = [_get_plot_info(p) for p in plots]
    df = pd.DataFrame(infos)
    return df

def build_plots():
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

    # load environmnet vars
    env_msg = 'Environment varibles not set {0}, try: export {0}=<some value>'

    access_key = environ.get('AWS_KEY_ID')
    if not access_key:
        raise ValueError(env_msg.format('AWS_KEY_ID'))

    secret_key = environ.get('AWS_SECRET_ID')
    if not secret_key:
        raise ValueError(env_msg.format('AWS_SECRET_ID'))

    upload_bucket = environ.get('TAXPLOT_S3_BUCKET')
    if not upload_bucket:
        raise ValueError(env_msg.format('TAXPLOT_S3_BUCKET'))

    print('Uploading Plots to: {0}'.format(upload_bucket))

    # upload plots
    plots_df = list_plots()
    s3_client = boto3.client('s3',
                             aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key)
    upload_func = partial(_upload_plot, s3_client, upload_bucket) 
    plots_df['plot_url'] = plots_df.apply(upload_func, axis=1)

    # log successful uploads
    success_df = plots_df[plots_df['plot_url'] != False]
    if not success_df.empty:
        print('\n\nSuccessfully Uploaded:')
        print('-------------------')
        print(success_df[['plot_name', 'plot_id', 'plot_url']])
        print('\n\n')

    # log error uploads
    error_df = plots_df[plots_df['plot_url'] == False]
    if not error_df.empty:
        print('\n\nErrors while uploading:')
        print('----------------------')
        print(error_df[['plot_name', 'plot_id']])
        print('\n\n')

