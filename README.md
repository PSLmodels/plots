# taxplots

A repository of visualizations for tax policy reforms.

### What is a taxplot?

A tax plot

### Create A Plot

### List Plots
```bash
list-plots
```

### Build Plots
```bash
build-plots
```

### Upload Plots
```bash
upload-plots
```

### info.yml
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

### Plot Resource Directory
Any supporting files (e.g. `.js`, `.css`, `.png`) should be placed in a `resources` directory within the plot directory. `Note`: All files placed in the `resources` will be uploaded/made-public to taxplots.

### Contributing a Plot
- fork this repository
- add a new plot directory to the `contrib` directory whose name should contain **no spaces**, or invalid url characters.
- to your new directory, add the `html file` which represents your plot
- submit a Pull Request to `taxplots`
