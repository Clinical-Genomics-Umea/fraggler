# Description of How the Figures Were Generated

## Figure 1
Figure 1 was assembled using parts from the Fraggler report generated from the `fraggler/demo/multiplex.fsa` file.

## Figure 2
Figure 2 was created using the .fsa files located in the `fraggler/paper/figures/data` folder.

Area ratios were generated using both Fraggler and the cloud version of Peakscanner on [Thermo Fisher](https://www.thermofisher.com).

### Fraggler 
The following command was run to create the peak area tables for each file:
`fraggler -t area -f fraggler/paper/figures/data -o fraggler_results -l LIZ -sc DATA1 -cp fraggler/paper/figures/data/custom_peaks.csv`

### Peakscanner
The Peakscanner dataframe was created by uploading the .fsa files from `fraggler/paper/figures/data` to Peakscanner. The resulting files were downloaded and merged into `fraggler/paper/figures/data/peakscanner_cnv.csv`.

### Script
The script `fraggler/paper/figures/fraggler_manuscript_plots.Rmd` was used to generate Figure 2.
