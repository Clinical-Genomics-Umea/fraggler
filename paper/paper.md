---
title: 'Fraggler: A Python Package and CLI Tool for Automated Fragment Analysis'
tags:
    - Paralouge ratio test
    - PRT
    - Fragment analysis
    - Bioinformatics
    - DNA analysis
    - Automation
    - Python
    - Fragment size determination
authors:
    - name: William Rosenbaum^[corresponding author]
      orcid: 0000-0003-2274-7343
      affiliation: "1, 2"
    - name: Pär Larsson
      affiliation: "2"
affiliations:
  - name: Department of Medical Biosciences, Umeå University, SE-90185, Umeå, Sweden
    index: 1
  - name: Clinical Genomics Umeå, Umeå University, SE-90185, Umeå, Sweden
    index: 2
date: 20 May 2024
bibliography: paper.bib
---

# Summary

Fragment Analysis (FA) is a PCR based technique which separates DNA fragments according to their sizes using a capillary electrophoresis instrument. PCR products are marked by fluorescent dyes and the intensities and migration time of the emitted signal are measured [@Van_Steenderen2022-dz;@Covarrubias-Pazaran2016-rj]. This enables a multitude of applications including Sanger sequencing, microsatellite marker analysis, multiplex ligation-dependent probe amplification assays, and more.   

Although Next Generation Sequencing (NGS) technologies are becoming more widely used in genetic research and clinical diagnosis, older PCR based techniques, such as FA, still play an important role due to its robustness and low cost [@McCafferty2012-gj;@Covarrubias-Pazaran2016-rj]. Even though NGS has many benefits over FA, FA is in many cases still the preferable choice, especially if the number of samples are limited or when genomic regions of interest are few [@Darby2016-ta]. Overall, FA is still a valuable tool due to its fast turnaround time, sensitivity, and cost.

We here provide `Fraggler` – a Python based software available both as a command line tool and a Python package for FA analysis. At its core, `Fraggler` generates easy to interpret `HTML` reports with plots and statistics for each `.fsa` file with FA data. Example of content in the report can be seen in \autoref{fig:combined_graph}.

As a test application for `Fraggler`, we used the Paralog Ratio Test (PRT) [@Algady2021-pa] that enables detection of copy number variations (CNVs). CNV can influence the phenotype of individuals due to gene dosage effects without changing the gene function [@McCarroll2007-ey;@Polley2015-pd]. Many examples of genes with various numbers of CNV exist, where the difference in CNV can affect the susceptibility to various infections [@Armour2007-aw;@Polley2015-pd;@Royo2015-mu]. PRT is used to quantify copy number differences using a single primer pair that amplifies targets both within and outside a multiplicated region, but result in different fragment sizes. The quotient of peak areas corresponding fragments from the reference region and the test region is calculated, allowing for inference of copy number differences [@Royo2015-mu]. PRT requires both size determination of fragments as well as quantification of peak areas, thus providing a suitable test case for `Fraggler`. 

![Example of content available in `Fraggler` generated report. (A) Examples of peak areas from PRT assay. (B) Linear model fitted to the included size standard. (C) Overview of all peaks found in the PRT assay. (D) Peaks used to fit the linear model to the size standard. (E) All channels shown in one figure for overview.\label{fig:combined_graph}](combined.png){ width=100% }

# Statement of Need

Despite the empirically known robustness of PRT analysis [@Algady2021-pa] and the widespread use of other FA applications, no reliable Python package exists to analyze FA data. Typically, the output from FA machines, in the form of _.fsa_ files, is analyzed using commercial software such as [GeneMapper](https://www.thermofisher.com/order/catalog/product/4475073) or [GeneMarker](https://softgenetics.com/products/genemarker/). Open-source alternatives like `Fragman` [@Covarrubias-Pazaran2016-rj] or free software such as [PeakScanner](https://www.thermofisher.com/order/catalog/product/4381867) are also available. However, these options are either proprietary, lack seamless integration into automated workflows, lack good documentation and relevant features.

We developed `Fraggler` to address all the aforementioned problems. Fraggler is entirely built in Python, it is open source and platform-independent, it allows for easy and rapid analysis of FA data, and is easy to integrate within automated workflows. Fraggler is designed for scalable automation and report generation of many samples from different FA applications and datasets, ensuring reproducibility for users with little or no background in bioinformatics. Documentation for `Fraggler` is provided at [https://clinical-genomics-umea.github.io/fraggler/fraggler.html](https://clinical-genomics-umea.github.io/fraggler/fraggler.html) and source code is available at [https://github.com/Clinical-Genomics-Umea/fraggler](https://github.com/Clinical-Genomics-Umea/fraggler). For ease of installation and use, `Fraggler` is available at [`pypi`](https://pypi.org/project/fraggler/). 

# Implementation

`Fraggler` can be used in two different ways: _(i)_ as a command-line interface (CLI) tool, or _(ii)_ as a Python package with an available application programming interface (API).

## Dependencies 

`Fraggler` relies on several stable and widely used external dependencies, many of which coming from the _Scipy_ ecosystem, such as `Pandas`, `Numpy`, `Scikit-learn` and `Scipy` [@Virtanen2020-vm]. 

Other commonly used external dependencies used by Fraggler are `Biopython` [@Cock2009-ai], `lmfit` [@Newville2014-no] and `Networkx` [@hagberg2008exploring].

## Features

### Peak Finding Algorithm

Peaks are determined using the _Signal_ module in `Scipy` [@Virtanen2020-vm]. Identified peaks are compared to the peak with the highest intensity, and only peaks with a height ratio above a user-defined threshold are returned as true peaks. The user can choose between customized peak-finding or agnostic peak-finding algorithms.

### Interpolate Basepairs from Migration Time

To find the correct peaks in the size-standard channel, all possible combinations of size-standard and ladder peaks are calculated using `Networkx` [@hagberg2008exploring].

Combinations of size-standards and ladder peak pairs with the highest correlation, calculated by the `corr` method in `Scipy` [@Virtanen2020-vm], are used to fit a spline-transformed linear regression model using `Scikit-learn` [@Pedregosa2012-fm]. The fitted model is used to predict time base pairs (bp), fitting the time-series data to the ladder peak values (\autoref{fig:combined_graph} B & D).

### Fit Area Model to Peaks

Here, widths of the identified peaks from the peak finding algorithm are used. The peak widths are used to separate the found peaks and include correct flanking regions to make plots and to fit models to the identified peaks.

To fit models to the peaks, built-in functions and methods of the `lmfit` library are used, which utilize non-linear least-squares minimization for curve fitting [@Newville2014-no]. The user can specify which model to use, choosing between _Voigt_, _Gaussian_, or _Lorentzian_. The peak area is returned from each fitted model given as an unit-normalized distribution. The unit-normalized distribution for each peak is used to calculate peak area ratios between peaks. Leveraging non-linear least-squares minimization mitigates the presence of stutter peaks, and only the assumed true peak is used to fit the model (\autoref{fig:combined_graph} A).

### Automated Reports

`Fraggler` implements a function for automated `HTML` reports for each sample analyzed, using the `panel` package.

## CLI

The CLI `Fraggler` tool is used to generate `HTML` reports for the input _.fsa_ files. The two subcommands are `fraggler area` and `fraggler peak`. Full documentation of the required and optional arguments can be found at [https://github.com/Clinical-Genomics-Umea/fraggler](https://github.com/Clinical-Genomics-Umea/fraggler). 

## Python API

`Fraggler` can be imported as a module in Python to be integrated into a larger workflow or used in a _Jupyter notebook_, for example.

Full documentation for the API can be found at [https://clinical-genomics-umea.github.io/fraggler/fraggler.html](https://clinical-genomics-umea.github.io/fraggler/fraggler.html). A [tutorial](https://github.com/Clinical-Genomics-Umea/fraggler/blob/main/tutorial.ipynb) exemplifying the API is also available.

# Benchmarking

We compared the peak area quotients generated by `Fraggler` and [PeakScanner](https://www.thermofisher.com/order/catalog/product/4381867) across four different PRT assays (\autoref{fig:comparison}). Reference CNVs are plotted on the y-axis, while the quotient of the test and reference area is plotted on the x-axis. The results depicted in \autoref{fig:comparison} are very similar, suggesting no apparent differences between the two softwares. However, one notable distinction for users lies in the usability of the two tools. Generating results with [PeakScanner](https://www.thermofisher.com/order/catalog/product/4381867) involves a manual procedure that consumes a significant amount of time, and the quotients need to be calculated separately. In contrast, the `Fraggler` procedure is fully automated, scales well and is hence suitable for clinical laboratories or other production laboratories.

![Comparison between `Fraggler` and [PeakScanner](https://www.thermofisher.com/order/catalog/product/4381867). The comparisons are made between four different PRT assays, 1-4.\label{fig:comparison}](cnv_ratio_fraggler_peakscanner_facet.tiff){ width=100% }

# Acknowledgements

We thank Nicklas Strömberg for stating the need for such a tool as `Fraggler`. We also thank Linda Köhn at Clinical Genomics in Umeå for testing `Fraggler` and for suggesting improvements and new features. We thank Ed Hollox in the University of Leicester for sending test data and answering questions about PRT. Also, we want to thank Dr. Lennart Österman for his valuable input during the development of `Fraggler`. Lastly, we want to thank Richard Palmqvist – the scientific director of Clinical Genomics in Umeå. Funding to support the development was provided by SciLifeLab Clinical Genomics Platform and Region Västerbotten.

# References