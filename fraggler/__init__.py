r"""
.. include:: ../README.md
.. include:: ../CONTRIBUTION.md
"""

__author__ = "William Rosenbaum and Pär Larsson"

from .ladder_fitting.fit_ladder_model import FitLadderModel
from .ladder_fitting.peak_ladder_assigner import PeakLadderAssigner
from .ladders.ladders import LADDERS
from .plotting.plot_ladder import PlotLadder
from .utils.baseline_removal import baseline_arPLS
from .utils.fsa_file import FsaFile
from .utils.utils import get_files, setup_logging
from .utils.fraggler_object import (
    FragglerPeak,
    FragglerArea,
    make_fraggler_peak,
    make_fraggler_area,
)
from .applications.peak_area_multiplex import PeakAreaDeMultiplex
from .plotting.plot_peak_area import PlotPeakArea
from .plotting.plot_raw_data import PlotRawData
from .plotting.plot_peaks import PlotPeaks
from .plotting.plot_channels import make_fsa_data_df, plot_fsa_data
from .reports.reports import (
    generate_peak_report,
    generate_area_report,
    generate_no_peaks_report,
)
from .functions.generate_peak_table import generate_peak_table
from .utils.peak_finder import PeakFinder
from .cli import peak_report, area_report


__all__ = [
    "FitLadderModel",
    "PeakLadderAssigner",
    "LADDERS",
    "baseline_arPLS",
    "FsaFile",
    "PeakArea",
    "PeakAreaDeMultiplex",
    "PlotPeakArea",
    "PlotLadder",
    "PlotRawData",
    "PlotPeaks",
    "generate_peak_table",
    "get_files",
    "setup_logging",
    "make_fsa_data_df",
    "plot_fsa_data",
    "PeakFinder",
    "FragglerPeak",
    "FragglerArea",
    "make_fraggler_peak",
    "make_fraggler_area",
    "generate_peak_report",
    "generate_area_report",
    "generate_no_peaks_report",
    "peak_report",
    "area_report",
]
