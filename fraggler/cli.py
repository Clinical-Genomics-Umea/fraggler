import fire
import pandas as pd
from pathlib import Path
import sys
import logging
from colorama import Fore as f, init
import matplotlib
import warnings
import platform

warnings.filterwarnings("ignore")

import fraggler

# from colorama
init(autoreset=True)

# for windows user
if platform.system() == "Windows":
    matplotlib.use("agg")

ASCII_ART = f"""{f.RED}
            █████▒██▀███   ▄▄▄        ▄████   ▄████  ██▓    ▓█████  ██▀███
          ▓██   ▒▓██ ▒ ██▒▒████▄     ██▒ ▀█▒ ██▒ ▀█▒▓██▒    ▓█   ▀ ▓██ ▒ ██▒
          ▒████ ░▓██ ░▄█ ▒▒██  ▀█▄  ▒██░▄▄▄░▒██░▄▄▄░▒██░    ▒███   ▓██ ░▄█ ▒
          ░▓█▒  ░▒██▀▀█▄  ░██▄▄▄▄██ ░▓█  ██▓░▓█  ██▓▒██░    ▒▓█  ▄ ▒██▀▀█▄
          ░▒█░   ░██▓ ▒██▒ ▓█   ▓██▒░▒▓███▀▒░▒▓███▀▒░██████▒░▒████▒░██▓ ▒██▒
           ▒ ░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ░▒   ▒  ░▒   ▒ ░ ▒░▓  ░░░ ▒░ ░░ ▒▓ ░▒▓░
           ░       ░▒ ░ ▒░  ▒   ▒▒ ░  ░   ░   ░   ░ ░ ░ ▒  ░ ░ ░  ░  ░▒ ░ ▒░
           ░ ░     ░░   ░   ░   ▒   ░ ░   ░ ░ ░   ░   ░ ░      ░     ░░   ░
                    ░           ░  ░      ░       ░     ░  ░   ░  ░   ░
"""


def save_df_format(
    peak_dfs: list,
    out_folder: str,
    in_path: str,
    out_format: str,
) -> None:
    # Save dataframe
    df = pd.concat(peak_dfs).reset_index(drop=True)
    out_name = f"{out_folder}/areatable_{Path(in_path).resolve().parts[-1]}"
    if out_format == "excel":
        df.to_excel(f"{out_name}.xlsx", index=False)
    elif out_format == "csv":
        df.to_csv(f"{out_name}.csv", index=False)
    elif out_format == "json":
        df.to_json(f"{out_name}.json")
    else:
        raise NotImplementedError("Choose between: csv, excel, json")


def area_report(
    in_path: str,
    out_folder: str,
    ladder: str,
    peak_model: str = "gauss",
    min_ratio: float = 0.2,
    min_height: int = 30,
    cutoff: int = 175,
    channel: str = "DATA1",
    peak_height: int = 500,
    size_standard_channel: str | None = None,
    distance_between_assays: int = 15,
    custom_peaks: str = None,
    out_format: str = "excel",
) -> None:

    print(ASCII_ART)
    if custom_peaks:
        peak_height = 0

    # Logging
    fraggler.setup_logging(out_folder)
    INFO = f"""
    Runned command:
    {' '.join(sys.argv)}

    Running fraggler with following parameters:
        In path: {in_path}
        Out folder: {out_folder}
        Ladder: {ladder}
        Peak model: {peak_model}
        Min ratio: {min_ratio}
        Min height: {min_height}
        Cutoff: {cutoff}
        Trace channel: {channel}
        Peak Height: {peak_height}
        Custom Peaks: {custom_peaks}
        Out format: {out_format}
        Size standard channel: {size_standard_channel}
        Distance between assays: {distance_between_assays}
    """
    logging.info(INFO)

    # Files
    files = fraggler.get_files(in_path)
    out_folder = Path(out_folder)

    # Generate a peak area report for each file
    failed_files = []
    no_peaks = []
    peak_dfs = []
    for file in files:
        logging.info(f"Processing file: {file}")
        fraggler_object = fraggler.make_fraggler_area(
            file=file,
            ladder=ladder,
            min_height=min_height,
            min_ratio=min_ratio,
            trace_channel=channel,
            distance_between_assays=distance_between_assays,
            size_standard_channel=size_standard_channel,
            cutoff=cutoff,
            peak_height=peak_height,
            custom_peaks=custom_peaks,
        )

        # If make_fraggler_object failed
        if isinstance(fraggler_object, str):
            failed_files.append(fraggler_object)
            fsa = fraggler.FsaFile(file, ladder)
            report = fraggler.generate_no_peaks_report(fsa)
            out_name = out_folder / f"{file.stem}_fraggler_failed.html"
            report.save(out_name)
            continue

        if not fraggler_object.peaks.found_peaks:
            no_peaks.append(file.stem)
            fsa = fraggler.FsaFile(file, ladder)
            report = fraggler.generate_no_peaks_report(fsa)
            out_name = out_folder / f"{file.stem}_failed.html"
            report.save(out_name)
            continue

        # generate report and peak table

        peak_dfs.append(fraggler_object.areas.assays_dataframe(peak_model))
        report = fraggler.generate_area_report(fraggler_object, peak_model)
        out_name = out_folder / f"{file.stem}_fraggler_area.html"
        report.save(out_name)

    # Save dataframe
    if peak_dfs:
        save_df_format(peak_dfs, out_folder, in_path, out_format)

    # log failed files
    logging.info(f"Fraggler done for files in {in_path}!")

    if failed_files:
        failed_files = "\n".join(failed_files)
        logging.warning(f"{f.YELLOW}Following files failed: {failed_files}")
    if no_peaks:
        no_peaks = "\n".join(no_peaks)
        logging.warning(f"{f.YELLOW}Following files had no peaks: {no_peaks}")


def peak_report(
    in_path: str,
    out_folder: str,
    ladder: str,
    min_ratio: float = 0.2,
    min_height: int = 30,
    channel: str = "DATA1",
    peak_height: int = 500,
    size_standard_channel: str | None = None,
    distance_between_assays: int = 15,
    custom_peaks: str = None,
    out_format: str = "excel",
) -> None:

    if custom_peaks:
        peak_height = 0

    print(ASCII_ART)

    # Logging
    fraggler.setup_logging(out_folder)
    INFO = f"""
    Runned command:
    {' '.join(sys.argv)}

    Running fraggler with following parameters:
        In path: {in_path}
        Out folder: {out_folder}
        Ladder: {ladder}
        Min ratio: {min_ratio}
        Min height: {min_height}
        Trace channel: {channel}
        Peak Height: {peak_height}
        Custom Peaks: {custom_peaks}
        Out format: {out_format}
        Size standard channel: {size_standard_channel}
        Distance between assays: {distance_between_assays}
    """
    logging.info(INFO)

    # Files
    files = fraggler.get_files(in_path)
    out_folder = Path(out_folder)

    # Generate a peak area report for each file
    failed_files = []
    no_peaks = []
    peak_dfs = []
    for file in files:
        logging.info(f"Processing file: {file}")
        fraggler_object = fraggler.make_fraggler_peak(
            file=file,
            ladder=ladder,
            min_height=min_height,
            min_ratio=min_ratio,
            trace_channel=channel,
            distance_between_assays=distance_between_assays,
            size_standard_channel=size_standard_channel,
            peak_height=peak_height,
            custom_peaks=custom_peaks,
        )

        # If make_fraggler_object failed
        if isinstance(fraggler_object, str):
            failed_files.append(fraggler_object)
            fsa = fraggler.FsaFile(file, ladder)
            report = fraggler.generate_no_peaks_report(fsa)
            out_name = out_folder / f"{file.stem}_fraggler_failed.html"
            report.save(out_name)
            continue

        if not fraggler_object.peaks.found_peaks:
            no_peaks.append(file.stem)
            fsa = fraggler.FsaFile(file, ladder)
            report = fraggler.generate_no_peaks_report(fsa)
            out_name = out_folder / f"{file.stem}_failed.html"
            report.save(out_name)
            continue

        # add peaks to dataframe
        df = fraggler_object.peaks.peak_information.assign(
            file_name=fraggler_object.fsa.file_name
        )[["file_name", "basepairs", "peaks"]].rename(columns={"peaks": "peak_height"})
        peak_dfs.append(df)

        # generate report
        report = fraggler.generate_peak_report(fraggler_object)
        out_name = out_folder / f"{file.stem}_fraggler_peak.html"
        report.save(out_name)

    # Save dataframe
    if peak_dfs:
        save_df_format(peak_dfs, out_folder, in_path, out_format)

    # log failed files
    logging.info(f"Fraggler done for files in {in_path}!")

    if failed_files:
        failed_files = "\n".join(failed_files)
        logging.warning(f"{f.YELLOW}Following files failed: {failed_files}")
    if no_peaks:
        no_peaks = "\n".join(no_peaks)
        logging.warning(f"{f.YELLOW}Following files had no peaks: {no_peaks}")


def run():
    """
    Run the command-line interface using Fire.
    """
    fire.Fire(
        {
            "area": area_report,
            "peak": peak_report,
        }
    )
