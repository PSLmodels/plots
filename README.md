# taxplots

A repository of visualizations for tax policy reforms.

### What is a taxplot?

TaxPlots are single html files which contain visual elements (e.g. images, charts, graphs) to  communicate an insight regarding the tax system.

### Installation

Install the taxplots package using the following commmand:

```bash
python setup.py install
```

TODO: Add conda recipe

### Create A Plot
#### info.yml
The `info.yml` file contains metadata for the plot and is required to contain the following key-value pairs:

```yml
plot_name: Tax Reform Explorer
plot_id: tax_reform_explorer
content: tax-reform-explorer.html
thumbnail: thumbnail.png
short_description: This plot shows a short amount of stuff
long_description: This plot shows a long amount of stuff
build_cmd: "python main.py"
```

#### resources directory
Any supporting files (e.g. `.js`, `.css`, `.png`) should be placed in a `resources` directory within the plot directory. 

**Note:** All files placed in the `resources` will be uploaded/made-public to taxplots.

### TaxPlot Command-line Tools
Install with the taxplots python package is a command-line interface (cli) which provides the following utilites:

#### List Plots
```bash
list-plots
```
TODO: Add content

#### Build Plots
```bash
build-plots
```
TODO: Add content

#### Upload Plots

The `upload-plots` cli tool will upload plots to an s3 bucket and including a `web_manifest.json` file which can be used to discover available plots from a 3rd Party applications.

```bash
upload-plots
```

To use the upload utility, you must have the following environment variables set:

```bash
    export AWS_KEY_ID=<my_aws_access_key>
    export AWS_SECRET_ID=<my_aws_secret_key>
    export TAXPLOT_S3_BUCKET=taxplots
```

TODO: Add content

### Contributing a Plot
- fork this repository
- add a new plot directory to the `contrib` directory whose name should contain **no spaces**, or invalid url characters.
- to your new directory, add the `html file` which represents your plot
- submit a Pull Request to `taxplots`
