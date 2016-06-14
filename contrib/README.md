# Contributing a Plot to `TaxPlots`

`Tax Plots` is a community-driven collection of visualizations pertaining to the tax system. We welcome contributions. Below are some guidelines for contributing:

Each plot has a corresponding directory in the `contrib` and should contain the following files:

 - `<my_final_plot>.html` (Required): Each plot should ultimately be a single HTML file.

 - `info.yml` (Required): Metadata file with plot information including:
   ```yml
	plot_name: This is the full name of the plot
	plot_id: tax_reform_explorer
	content: <my_final_plot>.html
	thumbnail: thumbnail.png
	short_description: This is a short description
	long_description: This is a longer description which is more detailed about the relevant take-aways from the plot.
	best_width: The recommended width for the plot (e.g. 500px, 25rem, 100%)
	best_height: The recommended height for the plot (e.g. 500px, 25rem, 100%)
	build_cmd: "python build.py"
   ```
   - Notice the `buildcmd` property in `info.yml`- this provides a bash command to execute to build your plot. This allows you to use web technologies which output HTML.  For example, Bokeh allows users to create plots using Python and render them to HTML Canvas or WebGL.  The `python build.py` command shown above will call my custom Python script which creates my plot's HTML file. While I used Python for the plot above, The `buildcmd` accepts any valid commnads which can be executed by Python's `os.system()` function.
    
 - `resources` (Optional): Directory with plot dependancies.  If your plot needs an external JS or CSS file, then place that file in the plot's `resources` directory along with any images or logos. When `TaxPlots` deploys your accepted plot into the gallery, these `resources` will also be deployed.

## Plot Contribution Checklist
1. Fork the `TaxPlots` repository into your own github account.
2. Clone your copy of `TaxPlots` to your local machine
3. Create your plot's directory in `taxplots/contrib` named using no spaces or non-ascii characters.
4. Inside the plot directory, create the `index.html` and `info.yml` files described above.
5. `git add`, `git commit`, `git push` your new plot back to your repository.
6. Submit a Pull Request to the `TaxPlots` github repository containing the new plot.  From there, we will review and merge you plot and it will be displayed in the `TaxPlot Gallery`.
