from setuptools import setup, find_packages

setup(
    name='Tax Plots',
    version='0.1.0',
    description='Create your own tax...plots',
    packages=find_packages(),
    entry_points = {
          'console_scripts': [
              'list-plots=taxplots.cli:list_plots',
              'build-plots=taxplots.cli:build_plots',
              'upload-plots=taxplots.cli:upload_plots'
          ],
      }
)
