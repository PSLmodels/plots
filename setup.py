from setuptools import setup, find_packages

setup(
    name='Tax Plots',
    version='0.1.0',
    description='create plots of tax information',
    packages=find_packages(),
    package_data={'': []},
    include_package_data=True,
    entry_points = {
          'console_scripts': [
              'build-plots=taxplots.build_plots:main'
              'upload-plots=taxplots.upload_plots:main'
          ],
      }
)
