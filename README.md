![Build Status](https://github.com/clinical-genomics-umea/fraggler/actions/workflows/pdoc.yaml/badge.svg)
[![!pypi](https://img.shields.io/pypi/v/fraggler?color=cyan)](https://pypi.org/project/fraggler/)
[![Download Status](https://static.pepy.tech/badge/fraggler)](https://pypi.python.org/pypi/fraggler/)

![logo](examples/logo.png)

## Description
Fraggler is for fragment analysis in Python!
Fraggler is a Python package that provides functionality for analyzing and generating reports for fsa files. It offers both a Python API and a command-line tool.

----------------

## Install

```bash
pip install fraggler
```

### Dependencies
Fraggler depends on:
- pandas
- numpy
- scikit-learn
- lmfit
- scipy
- biopython
- panel
- altair

## Python API

To get an overview how the library can be used in a python environment, please look at the [tutorial.ipynb](demo/tutorial.ipynb).


## CLI

#### Usage
To generate peak area reports and a peak table for all input files, use the `fraggler -t area` or `fraggler -t peak` command followed by the required arguments and any optional flags.

```bash
usage: fraggler [-h] -t {area,peak} -f FSA -o OUTPUT -l {LIZ,ROX,ORANGE,ROX500} -sc SAMPLE_CHANNEL
                 [-min_dist MIN_DISTANCE_BETWEEN_PEAKS] [-min_s_height MIN_SIZE_STANDARD_HEIGHT]
                 [-cp CUSTOM_PEAKS] [-height_sample PEAK_HEIGHT_SAMPLE_DATA]
                 [-min_ratio MIN_RATIO_TO_ALLOW_PEAK] [-distance DISTANCE_BETWEEN_ASSAYS]
                 [-peak_start SEARCH_PEAKS_START] [-m {gauss,voigt,lorentzian}]

Analyze your Fragment analysis files!

options:
  -h, --help            show this help message and exit
  -t {area,peak}, --type {area,peak}
                        Fraggler area or fraggler peak
  -f FSA, --fsa FSA     fsa file to analyze
  -o OUTPUT, --output OUTPUT
                        Output folder
  -l {LIZ,ROX,ORANGE,ROX500}, --ladder {LIZ,ROX,ORANGE,ROX500}
                        Which ladder to use
  -sc SAMPLE_CHANNEL, --sample_channel SAMPLE_CHANNEL
                        Which sample channel to use. E.g: 'DATA1', 'DATA2'...
  -min_dist MIN_DISTANCE_BETWEEN_PEAKS, --min_distance_between_peaks MIN_DISTANCE_BETWEEN_PEAKS
                        Minimum distance between size standard peaks
  -min_s_height MIN_SIZE_STANDARD_HEIGHT, --min_size_standard_height MIN_SIZE_STANDARD_HEIGHT
                        Minimun height of size standard peaks
  -cp CUSTOM_PEAKS, --custom_peaks CUSTOM_PEAKS
                        csv file with custom peaks to find
  -height_sample PEAK_HEIGHT_SAMPLE_DATA, --peak_height_sample_data PEAK_HEIGHT_SAMPLE_DATA
                        Minimum height of peaks in sample data
  -min_ratio MIN_RATIO_TO_ALLOW_PEAK, --min_ratio_to_allow_peak MIN_RATIO_TO_ALLOW_PEAK
                        Minimum ratio of the lowest peak compared to the heighest peak in the assay
  -distance DISTANCE_BETWEEN_ASSAYS, --distance_between_assays DISTANCE_BETWEEN_ASSAYS
                        Minimum distance between assays in a multiple assay experiment
  -peak_start SEARCH_PEAKS_START, --search_peaks_start SEARCH_PEAKS_START
                        Where to start searching for peaks in basepairs
  -m {gauss,voigt,lorentzian}, --peak_area_model {gauss,voigt,lorentzian}
                        Which peak finding model to use
```

##### Example of CLI command:
```bash
fraggler -t area -f demo/ -o testing_fraggler -l LIZ -sc DATA1
```

#### Peak finding
- If not specified, fraggler finds peaks agnostic in the `fsa file`. To specifiy custom assays with certain peaks and intervals, the user can add a .csv file to the `--custom_peaks` argument. The csv file **MUST** have the following shape:

| name | start | stop | amount | min_ratio | which | peak_distance |
|------|-------|------|--------|-----------|-------|---------------|
| prt1 | 140   | 150  | 2      | 0.2       | FIRST | 5             |

##### Example how how a file could look:
```txt 
name,start,stop,amount,min_ratio,which,peak_distance
prt1,135,155,2,0.2,FIRST,
prt3,190,205,,0.2,FIRST,
prt2,222,236,2,0.2,FIRST,5
prt4,262,290,5,,,
```

- `name`: Name of the assay
- `start`: Start of the assay in basepairs
- `stop`: Stop of the assay in basepairs
- `amount`: Optional. Amount of peaks in assay. If left empty every peak in the interval is included. 
- `min_ratio`: Optional. Only peaks with the a ratio of the `min_ratio` of the highest peak is included, *e.g.* if `min_ratio == .02`, only peaks with a height of 20 is included, if the highest peak is 100 units
- `which`: *LARGEST | FIRST*. Can be left empty. Which peak should be included if there are more peaks than the `amount`. if *FIRST* is set, then the two first peaks are chosen. If *LARGEST* are set, then the two largests peaks in the area are chosen. Defaults to *LARGEST*
- `peak_distance`: Optional. Distance between peaks must be ***under*** this value.


#### Documentation
Click [here](https://clinical-genomics-umea.github.io/fraggler/fraggler.html) to get full documentation of API.

## Output
One example of the report generated from `fraggler area` can be seen here: [Example report](examples/multiplex_fraggler_area.html)

## Contributions
Please check out [How to contribute](CONTRIBUTION.md)
