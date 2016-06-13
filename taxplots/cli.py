from __future__ import print_function, division, absolute_import

from functools import partial
from os import path, listdir, environ, system, walk
from pdb import set_trace

import mimetypes as mime
import pandas as pd

import boto3
import botocore

from taxplots.utils import ordered_load, DirectoryContext

contrib_dir = path.abspath(path.join(path.split(__file__)[0], '../contrib'))

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
    url_template = 'https://{0}.s3.amazonaws.com/{1}/{2}'

    with DirectoryContext(plot.directory) as dir_ctx:
        try:
            extra_args['ContentType'] = mime.guess_type(plot.content)[0]
            client.upload_file(plot.content, bucket,
                               path.join(plot.plot_id, plot.content),
                               ExtraArgs=extra_args)

            extra_args['ContentType'] = mime.guess_type(plot.thumbnail)[0]
            client.upload_file(plot.thumbnail, bucket,
                               path.join(plot.plot_id, plot.thumbnail),
                               ExtraArgs=extra_args)

            if path.exists('resources'):
                for dir_path, subdir_list, file_list in walk('resources'):
                    for fname in file_list:
                        full_path = path.join(dir_path, fname)
                        extra_args['ContentType'] = mime.guess_type(full_path)[0]
                        client.upload_file(full_path, bucket,
                                           path.join(plot.plot_id, full_path),
                                           ExtraArgs=extra_args)

            results = [url_template.format(bucket, plot.plot_id, plot.content),
                       url_template.format(bucket, plot.plot_id, plot.thumbnail)]

            return pd.Series(results)

        except botocore.exceptions.ClientError as e:
            print(e.response)
            return False

def _list_plots():
    global contrib_dir

    if not path.exists(contrib_dir):
        raise IOError("Can't find contrib directory: {0}".format(contrib_dir))

    plots = [path.join(contrib_dir, d) for d in listdir(contrib_dir)]
    infos = [_get_plot_info(p) for p in plots if path.isdir(p)]
    df = pd.DataFrame(infos)
    return df

def list_plots():
    plots_df = _list_plots()

    def print_plot(p):
        print('\n\n')
        print(p['plot_name'])
        print('-' * len(p.plot_name) + '\n')

        fields = ('plot_id',
                  'content',
                  'thumbnail',
                  'short_description',
                  'build_cmd')

        for f in fields:
            print('{} : {}'.format(f, p.get(f)) + '\n')

    plots_df.apply(print_plot, axis=1)

def build_plots():
    plots_df = _list_plots()
    plots_df['build_successful'] = plots_df.apply(_run_plot, axis=1)

    # log successful builds
    success_df = plots_df[plots_df['build_successful'] == True]
    if not success_df.empty:
        print('\n\nSuccessfully Built:')
        print('-------------------')
        print(success_df[['plot_name', 'plot_id', 'build_cmd']])
        print('\n\n')

    # log error builds
    error_df = plots_df[plots_df['build_successful'] == False]
    if not error_df.empty:
        print('\n\nErrors while Building:')
        print('----------------------')
        print(error_df[['plot_name', 'plot_id', 'build_cmd']])
        print('\n\n')

def _create_web_manifest(plots_df, s3_client, bucket):
    manifest_fields = ['plot_url', 'plot_name','plot_id','thumbnail_url']

    json_str = plots_df.reset_index()[manifest_fields].to_json(orient='records')
    web_manifest_path = path.join(contrib_dir, 'webmanifest.json')
    with open(web_manifest_path, 'w') as f:
        f.write(json_str)

    extra_args = dict(ACL='public-read', ContentType='application/json')
    s3_client.upload_file(web_manifest_path,
                          bucket,
                          'webmanifest.json',
                          ExtraArgs=extra_args)



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
    plots_df = _list_plots()
    s3_client = boto3.client('s3',
                             aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key)
    upload_func = partial(_upload_plot, s3_client, upload_bucket) 
    plots_df[['plot_url', 'thumbnail_url']] = plots_df.apply(upload_func, axis=1)

    # log successful uploads
    success_df = plots_df[plots_df['plot_url'] != False]
    if not success_df.empty:
        print('\n\nSuccessfully Uploaded:')
        print('-------------------')
        print(success_df[['plot_name', 'plot_id', 'plot_url']])
        print('\n\n')

        _create_web_manifest(success_df, s3_client, upload_bucket)

    # log error uploads
    error_df = plots_df[plots_df['plot_url'] == False]
    if not error_df.empty:
        print('\n\nErrors while uploading:')
        print('----------------------')
        print(error_df[['plot_name', 'plot_id']])
        print('\n\n')
