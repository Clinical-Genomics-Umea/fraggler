import panel as pn
from pathlib import Path
import datetime
import pandas as pd

from ..utils.peak_finder import PeakFinder
from ..utils.fraggler_object import (
    FragglerPeak,
    FragglerArea,
    make_fraggler_peak,
    make_fraggler_area,
)
from ..utils.fsa_file import FsaFile
from ..plotting.plot_channels import plot_fsa_data
from ..plotting.plot_peaks import PlotPeaks
from ..plotting.plot_ladder import PlotLadder


pn.extension("tabulator")
pn.extension("vega", sizing_mode="stretch_width", template="fast")
pn.widgets.Tabulator.theme = "modern"


def header(
    text: str,
    bg_color: str = "#04c273",
    height: int = 300,
    fontsize: str = "px20",
    textalign: str = "center",
):
    """
    Template for markdown header like block
    """
    return pn.pane.Markdown(
        f"""
        {text}
        """,
        background=bg_color,
        height=height,
        margin=10,
        style={
            "color": "white",
            "padding": "10px",
            "text-align": f"{textalign}",
            "font-size": f"{fontsize}",
        },
    )


def make_header(name: str, date: str) -> pn.pane.Markdown:
    return header(
        text=f"""
        # Fragment Analysis Report
        ## Report of {name}
        ## Date: {date}
        """,
        fontsize="20px",
        bg_color="#03a1fc",
        height=250,
    )


def generate_peak_report(fraggler: FragglerPeak) -> pn.layout.base.Column:
    ### ----- Raw Data ----- ###
    channel_header = header(
        text="## Plot of channels",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )
    # PLOT
    channel_tab = pn.Tabs()
    for plot, name in plot_fsa_data(fraggler.fsa):
        pane = pn.pane.Vega(plot.interactive(), sizing_mode="stretch_both", name=name)
        channel_tab.append(pane)

    channels_section = pn.Column(channel_header, channel_tab)

    ### ----- Peaks ----- ###
    peaks_header = header(
        text="## Plot of Peaks",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )

    # PLOT
    peaks_plot = PlotPeaks(fraggler.peaks).plot_peaks
    peaks_pane = pn.pane.Matplotlib(peaks_plot, name="Peaks")

    # Section
    peaks_tab = pn.Tabs(
        peaks_pane,
    )
    peaks_section = pn.Column(peaks_header, peaks_tab)

    ### ----- Ladder Information ----- ###
    ladder_header = header(
        text="## Information about the ladder",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )
    # Ladder peak plot
    ladder_plot = PlotLadder(fraggler.model)
    ladder_peak_plot = pn.pane.Matplotlib(
        ladder_plot.plot_ladder_peaks,
        name="Ladder Peak Plot",
    )
    # Ladder Correlation
    ladder_correlation_plot = pn.pane.Matplotlib(
        ladder_plot.plot_model_fit,
        name="Ladder Correlation Plot",
    )

    # Section
    ladder_tab = pn.Tabs(
        ladder_peak_plot,
        ladder_correlation_plot,
    )
    ladder_section = pn.Column(ladder_header, ladder_tab)

    ### ----- Peaks dataframe ----- ###
    dataframe_header = header(
        text="## Peaks Table", bg_color="#04c273", height=80, textalign="left"
    )
    # Create dataframe
    df = fraggler.peaks.peak_information.assign(file_name=fraggler.fsa.file_name)[
        ["file_name", "basepairs", "peaks", "assay_name"]
    ].rename(columns={"peaks": "peak_height"})
    # DataFrame Tabulator
    peaks_df_tab = pn.widgets.Tabulator(
        df,
        layout="fit_columns",
        pagination="local",
        page_size=15,
        show_index=False,
        name="Peaks Table",
    )

    # Section
    dataframe_tab = pn.Tabs(peaks_df_tab)
    dataframe_section = pn.Column(dataframe_header, dataframe_tab)

    ### CREATE REPORT ###

    file_name = fraggler.fsa.file_name
    date = fraggler.fsa.fsa["RUND1"]
    head = make_header(file_name, date)

    all_tabs = pn.Tabs(
        ("Channels", channels_section),
        ("Peaks", peaks_section),
        ("Ladder", ladder_section),
        ("Peaks Table", dataframe_section),
        tabs_location="left",
    )
    report = pn.Column(
        head,
        pn.layout.Divider(),
        all_tabs,
    )

    return report


def generate_area_report(
    fraggler: FragglerArea,
    peak_model: str = "gauss",
) -> pn.layout.base.Column:

    ### ----- Raw Data ----- ###
    channel_header = header(
        text="## Plot of channels",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )
    # PLOT
    channel_tab = pn.Tabs()
    for plot, name in plot_fsa_data(fraggler.fsa):
        pane = pn.pane.Vega(plot.interactive(), sizing_mode="stretch_both", name=name)
        channel_tab.append(pane)

    channels_section = pn.Column(channel_header, channel_tab)

    ### ----- Peaks ----- ###
    peaks_header = header(
        text="## Plot of Peaks",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )

    # PLOT
    peaks_plot = PlotPeaks(fraggler.peaks).plot_peaks
    peaks_pane = pn.pane.Matplotlib(peaks_plot, name="Peaks")

    # Section
    peaks_tab = pn.Tabs(
        peaks_pane,
    )
    peaks_section = pn.Column(peaks_header, peaks_tab)

    ### ----- Ladder Information ----- ###
    ladder_header = header(
        text="## Information about the ladder",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )
    # Ladder peak plot
    ladder_plot = PlotLadder(fraggler.model)
    ladder_peak_plot = pn.pane.Matplotlib(
        ladder_plot.plot_ladder_peaks,
        name="Ladder Peak Plot",
    )
    # Ladder Correlation
    ladder_correlation_plot = pn.pane.Matplotlib(
        ladder_plot.plot_model_fit,
        name="Ladder Correlation Plot",
    )

    # Section
    ladder_tab = pn.Tabs(
        ladder_peak_plot,
        ladder_correlation_plot,
    )
    ladder_section = pn.Column(ladder_header, ladder_tab)

    ### ----- Areas Information ----- ###
    areas_header = header(
        text="## Peak Areas", bg_color="#04c273", height=80, textalign="left"
    )
    areas_tab = pn.Tabs()
    for i, plot in enumerate(fraggler.areas.area_plots):
        name = f"Assay {i + 1}"
        plot_pane = pn.pane.Matplotlib(plot, name=name)
        areas_tab.append(plot_pane)

    # Section
    areas_section = pn.Column(areas_header, areas_tab)

    ### ----- Peaks DataFrame ----- ###
    dataframe_header = header(
        text="## Peaks Table", bg_color="#04c273", height=80, textalign="left"
    )

    if not hasattr(fraggler.areas, "final_df"):
        df = fraggler.areas.assays_dataframe(peak_model)
    else:
        df = fraggler.areas.final_df

    # DataFrame Tabulator
    peaks_df_tab = pn.widgets.Tabulator(
        df,
        layout="fit_columns",
        pagination="local",
        page_size=15,
        show_index=False,
        name="Peaks Table",
    )

    # Section
    dataframe_tab = pn.Tabs(peaks_df_tab)
    dataframe_section = pn.Column(dataframe_header, dataframe_tab)

    ### CREATE REPORT ###

    file_name = fraggler.fsa.file_name
    date = fraggler.fsa.fsa["RUND1"]
    head = make_header(file_name, date)

    all_tabs = pn.Tabs(
        ("Channels", channels_section),
        ("Peaks", peaks_section),
        ("Ladder", ladder_section),
        ("Areas", areas_section),
        ("Peak Table", dataframe_section),
        tabs_location="left",
    )
    report = pn.Column(
        head,
        pn.layout.Divider(),
        all_tabs,
    )

    return report


def generate_no_peaks_report(fsa: FsaFile):
    channel_header = header(
        text="## Plot of channels",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )
    # PLOT
    channel_tab = pn.Tabs()
    for plot, name in plot_fsa_data(fsa):
        pane = pn.pane.Vega(plot.interactive(), sizing_mode="stretch_both", name=name)
        channel_tab.append(pane)
    channels_section = pn.Column(channel_header, channel_tab)

    ### CREATE REPORT ###
    file_name = fsa.file_name
    date = fsa.fsa["RUND1"]
    head = header(
        "# No peaks could be generated. Please look at the raw data.", height=100
    )

    all_tabs = pn.Tabs(
        ("Channels", channels_section),
        tabs_location="left",
    )
    report = pn.Column(
        head,
        pn.layout.Divider(),
        all_tabs,
    )

    return report
