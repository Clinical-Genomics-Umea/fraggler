# TODO: add rere.py as testing
# Make a script and print the results in the terminal and capture it!


class bcolors:
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    UNDERLINE = "\033[4m"


def print_green(text):
    print(f"{bcolors.OKGREEN}[INFO]: {text}{bcolors.ENDC}")


def print_warning(text):
    print(f"{bcolors.WARNING}{bcolors.UNDERLINE}[WARNING]: {text}{bcolors.ENDC}")


def print_fail(text):
    print(f"{bcolors.FAIL}{bcolors.UNDERLINE}[ERROR]: {text}{bcolors.ENDC}")


def print_blue(text):
    print(f"{bcolors.OKBLUE}[SUMMARIZE]: {text}{bcolors.ENDC}")


print_green(f"Starting fraggler, importing libraries...")

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer
from sklearn.metrics import mean_squared_error, r2_score
from scipy.interpolate import UnivariateSpline
from pathlib import Path
from scipy import sparse
from scipy.sparse import linalg
from numpy.linalg import norm
from Bio import SeqIO
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd
import altair as alt
from lmfit.models import VoigtModel, GaussianModel, LorentzianModel
import re
import sys
from datetime import datetime
import argparse
import warnings
import platform
import panel as pn
import pandas_flavor as pf


warnings.filterwarnings("ignore")
# for windows user
if platform.system() == "Windows":
    matplotlib.use("agg")


from .ladders import LADDERS

### UTILITY FUNCTIONS ###
@pf.register_dataframe_method
def pivot_wider(
    df_: pd.DataFrame, index: list, names_from: list, values_from: list
) -> pd.DataFrame:
    df = df_.pivot(index=index, columns=names_from, values=values_from).reset_index()
    names = [[str(y) for y in x] for x in df.columns]
    names = ["_".join(x).strip("_") for x in names]
    df.columns = names

    return df


def baseline_arPLS(y, ratio=0.99, lam=100, niter=1000, full_output=False):
    """
    Taken from:
    https://stackoverflow.com/questions/29156532/python-baseline-correction-library

    from this paper:
    https://pubs.rsc.org/en/content/articlelanding/2015/AN/C4AN01061B#!divAbstract
    """
    L = len(y)

    diag = np.ones(L - 2)
    D = sparse.spdiags([diag, -2 * diag, diag], [0, -1, -2], L, L - 2)

    H = lam * D.dot(D.T)  # The transposes are flipped w.r.t the Algorithm on pg. 252

    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)

    crit = 1
    count = 0

    while crit > ratio:
        z = linalg.spsolve(W + H, W * y)
        d = y - z
        dn = d[d < 0]

        m = np.mean(dn)
        s = np.std(dn)

        w_new = 1 / (1 + np.exp(2 * (d - (2 * s - m)) / s))

        crit = norm(w_new - w) / norm(w)

        w = w_new
        W.setdiag(w)  # Do not create a new matrix, just update diagonal values

        count += 1

        if count > niter:
            print("Maximum number of iterations exceeded")
            break

    if full_output:
        info = {"num_iter": count, "stop_criterion": crit}
        return z, d, info
    else:
        return z


def make_dir(outpath: str) -> None:
    outpath = Path(outpath)
    if not outpath.exists():
        outpath.mkdir(parents=True)


def get_files(in_path: str) -> list[Path]:
    # If in_path is a directory, get a list of all .fsa files in it
    if Path(in_path).is_dir():
        files = [x for x in Path(in_path).iterdir() if x.suffix == ".fsa"]
    else:
        files = [Path(in_path)]
    return files


def file_exists(file):
    if not Path(file).exists():
        print_fail(f"{file} does not exist!")
        sys.exit(1)


def folder_exists(folder):
    if Path(folder).exists():
        print_fail(f"{folder} already exist!")
        sys.exit(1)


ASCII_ART = f"""{bcolors.OKBLUE}
            █████▒██▀███   ▄▄▄        ▄████   ▄████  ██▓    ▓█████  ██▀███
          ▓██   ▒▓██ ▒ ██▒▒████▄     ██▒ ▀█▒ ██▒ ▀█▒▓██▒    ▓█   ▀ ▓██ ▒ ██▒
          ▒████ ░▓██ ░▄█ ▒▒██  ▀█▄  ▒██░▄▄▄░▒██░▄▄▄░▒██░    ▒███   ▓██ ░▄█ ▒
          ░▓█▒  ░▒██▀▀█▄  ░██▄▄▄▄██ ░▓█  ██▓░▓█  ██▓▒██░    ▒▓█  ▄ ▒██▀▀█▄
          ░▒█░   ░██▓ ▒██▒ ▓█   ▓██▒░▒▓███▀▒░▒▓███▀▒░██████▒░▒████▒░██▓ ▒██▒
           ▒ ░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ░▒   ▒  ░▒   ▒ ░ ▒░▓  ░░░ ▒░ ░░ ▒▓ ░▒▓░
           ░       ░▒ ░ ▒░  ▒   ▒▒ ░  ░   ░   ░   ░ ░ ░ ▒  ░ ░ ░  ░  ░▒ ░ ▒░
           ░ ░     ░░   ░   ░   ▒   ░ ░   ░ ░ ░   ░   ░ ░      ░     ░░   ░
                    ░           ░  ░      ░       ░     ░  ░   ░  ░   ░{bcolors.ENDC}
"""


### FSA ###


class FsaFile:
    def __init__(
        self,
        file: str,
        ladder: str,
        sample_channel: str,
        min_distance_between_peaks: int,
        min_size_standard_height: int,
        normalize: bool = False,
    ) -> None:
        self.file = Path(file)
        self.file_name = self.file.parts[-1]

        if ladder not in LADDERS.keys():
            raise LadderNotFoundError(f"'{ladder}' is not a valid ladder")
            exit(1)
        self.ladder = ladder
        self.fsa = SeqIO.read(file, "abi").annotations["abif_raw"]
        self.sample_channel = sample_channel
        self.normalize = normalize

        self.ladder_steps = LADDERS[ladder]["sizes"]
        self.n_ladder_peaks = self.ladder_steps.size

        self.min_size_standard_height = min_size_standard_height
        self.size_standard_channel = self.find_size_standard_channel()
        self.min_distance_between_peaks = min_distance_between_peaks
        self.max_peaks_allow_in_size_standard = self.n_ladder_peaks + 5

        ### properties updateded by external functions

        # size standard peaks
        self.size_standard_peaks = None
        self.maxium_allowed_distance_between_size_standard_peaks = None
        self.best_size_standard_combinations = None
        self.best_size_standard = None

        # sample data with fitted basepairs
        self.fitted_to_model = False
        self.sample_data_with_basepairs = None
        self.ladder_model = None

        # updated by peak finder functions
        self.sample_data_peaks_raw = None
        self.identified_sample_data_peaks = None
        self.found_peaks = False

        # peak widths
        self.sample_data_peak_widths = None
        self.peaks_with_padding = None

        # area peaks
        self.fitted_area_peaks = None

        if normalize:
            self.size_standard = np.array(
                baseline_arPLS(self.fsa[self.size_standard_channel])
            )
            self.sample_data = np.array(baseline_arPLS(self.fsa[sample_channel]))
        else:
            self.size_standard = np.array(self.fsa[self.size_standard_channel])
            self.sample_data = np.array(self.fsa[self.sample_channel])

    def find_size_standard_channel(
        self,
        degree=2,
    ):

        data_channels = [x for x in self.fsa.items() if "DATA" in x[0]]
        best_r2 = 0
        best_fitted = None

        for i, data in enumerate(data_channels):
            array = signal.find_peaks(data[1], height=self.min_size_standard_height)[0]

            if len(array) < 12:
                continue
            X = np.arange(len(array)).reshape(-1, 1)
            poly = PolynomialFeatures(degree=degree)
            X_poly = poly.fit_transform(X)
            model = LinearRegression().fit(X_poly, array)
            predicted = model.predict(X_poly)
            r2 = r2_score(array, predicted)

            if r2 > best_r2:
                best_fitted = data[0]

        return best_fitted

    def __repr__(self):
        return f"""
            Filename: {self.file_name}
            Sample Channel: {self.sample_channel}
            Size Standard Channel: {self.size_standard_channel}
            Ladder Name: {self.ladder}
            Number of Ladder Steps: {self.n_ladder_peaks}
            Minimum Distance Between Peaks: {self.min_distance_between_peaks}
            Minimum Size Standard Height: {self.min_size_standard_height}
            Normalized Data: {self.normalize}
            Ladder Steps: {self.ladder_steps}
            Fitted to model: {self.fitted_to_model}
            Found peaks: {self.found_peaks}
            """


def find_size_standard_peaks(fsa):
    found_peaks = signal.find_peaks(
        fsa.size_standard,
        height=fsa.min_size_standard_height,
        distance=fsa.min_distance_between_peaks,
    )

    peaks = found_peaks[0]
    heights = found_peaks[1]["peak_heights"]

    size_standard_peaks = (
        pd.DataFrame({"peaks": peaks, "heights": heights})
        .sort_values("heights", ascending=False)
        .head(fsa.max_peaks_allow_in_size_standard)
        .sort_values("peaks")["peaks"]
        .to_numpy()
    )
    fsa.size_standard_peaks = size_standard_peaks
    return fsa


def return_maxium_allowed_distance_between_size_standard_peaks(fsa, multiplier=2):
    """
    Finds the average distance between peaks and
    multiplies the number with multiplier
    """
    peaks = fsa.size_standard_peaks
    max_distance = int(
        np.mean([peaks[i + 1] - peaks[i] for i in range(len(peaks) - 1)]) * multiplier
    )
    fsa.maxium_allowed_distance_between_size_standard_peaks = max_distance
    return fsa


def generate_combinations(fsa):
    """
    depth-first search
    """
    a = fsa.size_standard_peaks
    length = fsa.n_ladder_peaks
    distance = fsa.maxium_allowed_distance_between_size_standard_peaks
    memo = {}

    def dfs(start, path_len, path):
        if path_len == length:
            return [[]]

        if (start, path_len) in memo:
            return memo[(start, path_len)]

        result = []
        for i in range(start, len(a)):
            if not path or abs(a[i] - path[-1]) <= distance:
                for combo in dfs(i + 1, path_len + 1, path + [a[i]]):
                    result.append([a[i]] + combo)

        memo[(start, path_len)] = result
        return result

    best_combinations = pd.DataFrame({"combinations": dfs(0, 0, [])})
    fsa.best_size_standard_combinations = best_combinations
    return fsa


def calculate_best_combination_of_size_standard_peaks(fsa):
    """
    Finds the best size standard combination of all using UnivariateSpline and second derivative
    """
    combinations = fsa.best_size_standard_combinations

    best_combinations = (
        combinations.assign(
            der=lambda x: [
                UnivariateSpline(fsa.ladder_steps, y, s=0).derivative(n=2)
                for y in x.combinations
            ]
        )
        .assign(max_value=lambda x: [max(abs(y(fsa.ladder_steps))) for y in x.der])
        .sort_values("max_value", ascending=True)
    )

    best_size_standard = np.array(best_combinations.head(1).combinations.squeeze())
    fsa.best_size_standard = best_size_standard
    return fsa


def fit_size_standard_to_ladder(fsa) -> tuple:
    """
    Returns the FsaFile with updated model and datafram with sample data
    and fitted baisepairs.
    Increase the knots until every basepair is unique.
    """
    best_combination = fsa.best_size_standard
    n_knots = 4
    for _ in range(20):
        model = make_pipeline(
            SplineTransformer(degree=3, n_knots=n_knots, extrapolation="continue"),
            LinearRegression(fit_intercept=True),
        )

        X = best_combination.reshape(-1, 1)
        y = fsa.ladder_steps
        model.fit(X, y)

        sample_data_with_basepairs = (
            pd.DataFrame({"peaks": fsa.sample_data})
            .reset_index()
            .rename(columns={"index": "time"})
            .assign(basepairs=lambda x: model.predict(x.time.to_numpy().reshape(-1, 1)))
            .assign(basepairs=lambda x: x.basepairs.round(2))
            .loc[lambda x: x.basepairs >= 0]
        )

        if (
            sample_data_with_basepairs.shape[0]
            == sample_data_with_basepairs.basepairs.nunique()
        ):
            fsa.ladder_model = model
            fsa.sample_data_with_basepairs = sample_data_with_basepairs
            fsa.fitted_to_model = True
            return fsa
        else:
            n_knots += 1


### PLOTTING ###
def plot_areas(fsa):
    def plot_helper(identified_peaks, df):
        fig_areas, axs = plt.subplots(
            1, len(identified_peaks), sharey=True, figsize=(20, 10)
        )
        # if there is only one peak
        if len(identified_peaks) == 1:
            axs.plot(df.basepairs, df.peaks, "o")
            axs.plot(df.basepairs, df.fitted)
            axs.set_title(f"Peak 1 area: {df['amplitude'].iloc[0]: .1f}")
            axs.grid()
        # if more than one peak
        else:
            peaks = [df.loc[lambda x: x.peak_name == p] for p in df.peak_name.unique()]
            for i, ax in enumerate(axs):
                ax.plot(
                    peaks[i].basepairs,
                    peaks[i].peaks,
                    "o",
                )
                ax.plot(peaks[i].basepairs, peaks[i].fitted)
                ax.set_title(f"Peak {i + 1} area: {peaks[i]['amplitude'].iloc[0]: .1f}")
                ax.grid()

        fig_areas.suptitle(f"Quotient: {df['quotient'].iloc[0]: .2f}")
        fig_areas.legend(["Raw data", "Model"])
        fig_areas.supxlabel("Basepairs")
        fig_areas.supylabel("Intensity")
        plt.close()

        return fig_areas

    plots = []
    for a in fsa.identified_sample_data_peaks.assay.unique():

        identified_peaks = fsa.identified_sample_data_peaks.loc[lambda x: x.assay == a]
        df = fsa.fitted_area_peaks.loc[lambda x: x.assay == a]
        plot = plot_helper(identified_peaks, df)
        plots.append(plot)

    return plots


def make_fsa_data_df(fsa) -> pd.DataFrame:
    data_channels = [x[0] for x in fsa.fsa.items() if "DATA" in x[0]]
    dfs = []
    for d in data_channels:
        df = (
            pd.DataFrame()
            .assign(data=fsa.fsa[d])
            .assign(channel=d)
            .assign(time=lambda x: range(x.shape[0]))
        )
        dfs.append(df)
    return pd.concat(dfs)


def plot_fsa_data(fsa) -> list:
    alt.data_transformers.disable_max_rows()
    df = make_fsa_data_df(fsa)

    plots = []
    for channel in df.channel.unique():
        plot = (
            alt.Chart(df.loc[lambda x: x.channel == channel])
            .mark_line()
            .encode(
                alt.X("time:Q", title="Time"),
                alt.Y("data:Q", title="Intensity"),
                alt.Color("channel:N"),
            )
            .properties(
                width=800,
                height=500,
            )
            .interactive()
        )
        plots.append((plot, channel))

    all_data = (
        alt.Chart(df)
        .mark_line()
        .encode(
            alt.X("time:Q", title="Time"),
            alt.Y("data:Q", title="Intensity"),
            alt.Color("channel:N"),
        )
        .properties(
            width=800,
            height=500,
        )
        .interactive()
    )
    plots.append((all_data, "All channels"))
    return plots


def plot_all_found_peaks(fsa):
    fig_peaks = plt.figure(figsize=(20, 10))

    df = fsa.sample_data_peaks_raw.loc[
        lambda x: x.basepairs > fsa.identified_sample_data_peaks.basepairs.min() - 10
    ].loc[lambda x: x.basepairs < fsa.identified_sample_data_peaks.basepairs.max() + 10]

    plt.plot(df.basepairs, df.peaks)
    plt.plot(
        fsa.identified_sample_data_peaks.basepairs,
        fsa.identified_sample_data_peaks.peaks,
        "o",
    )
    for x, y in zip(
        fsa.identified_sample_data_peaks.basepairs,
        fsa.identified_sample_data_peaks.peaks,
    ):
        plt.text(x, y, f"{round(x, 1)} bp")

    plt.title(f"Channel: {fsa.sample_channel}")
    plt.xticks(np.arange(df.basepairs.min(), df.basepairs.max(), 10), rotation=90)
    plt.ylabel("intensity")
    plt.xlabel("basepairs")
    plt.grid()
    plt.close()

    return fig_peaks


def plot_size_standard_peaks(fsa):
    best_combination = fsa.best_size_standard
    size_standard = fsa.size_standard
    ladder_name = fsa.ladder
    ladder_size = fsa.ladder_steps

    fig_ladder_peaks = plt.figure(figsize=(20, 10))
    plt.plot(size_standard)
    plt.plot(best_combination, size_standard[best_combination], "o")
    plt.xlabel("Time")
    plt.ylabel("Intensity")
    plt.legend(["Size standard", "Peak (bp)"])
    plt.title(ladder_name)
    plt.grid()

    for peak, ladder in zip(best_combination, ladder_size):
        plt.text(peak, size_standard[peak], ladder)

    plt.close()
    return fig_ladder_peaks


def plot_model_fit(fsa):
    ladder_size = fsa.ladder_steps
    best_combination = fsa.best_size_standard

    predicted = fsa.ladder_model.predict(best_combination.reshape(-1, 1))
    ladder_name = fsa.ladder

    mse = mean_squared_error(ladder_size, predicted)
    r2 = r2_score(ladder_size, predicted)

    fig_model_fit = plt.figure(figsize=(20, 10))
    plt.plot(ladder_size, best_combination, "o")
    plt.plot(predicted, best_combination, "x")
    plt.xticks(np.arange(0, np.max(ladder_size), 50))
    plt.xlabel("bp")
    plt.yticks(np.arange(0, np.max(best_combination), 500))
    plt.suptitle(ladder_name)
    plt.title(f"Mean squared error: {mse: .3f}, R2: {r2: .5f}")
    plt.legend(["True value", "Predicted value"])
    plt.grid()

    plt.close()
    return fig_model_fit


### PEAK FINDING ###
def find_peaks_agnostic(
    fsa,
    peak_height_sample_data: int,
    min_ratio: float,
    distance_between_assays: int,
    search_peaks_start: int,
):

    peaks_dataframe = fsa.sample_data_with_basepairs.loc[
        lambda x: x.basepairs > search_peaks_start
    ]
    peaks_index, _ = signal.find_peaks(
        peaks_dataframe.peaks, height=peak_height_sample_data
    )

    identified_peaks = (
        peaks_dataframe.iloc[peaks_index]
        .assign(peaks_index=peaks_index)
        .assign(peak_name=lambda x: range(1, x.shape[0] + 1))
        # separate the peaks into different assay groups depending on the distance
        # between the peaks
        .assign(difference=lambda x: x.basepairs.diff())
        .fillna(100)
        .assign(
            assay=lambda x: np.select(
                [x.difference > distance_between_assays],
                [x.peak_name * 10],
                default=pd.NA,
            )
        )
        .fillna(method="ffill")
        .assign(max_peak=lambda x: x.groupby("assay")["peaks"].transform(np.max))
        .assign(ratio=lambda x: x.peaks / x.max_peak)
        .loc[lambda x: x.ratio > min_ratio]
        .assign(peak_name=lambda x: range(1, x.shape[0] + 1))
    )

    if identified_peaks.shape[0] == 0:
        # TODO: REWRITE
        print("No peaks could be found")
        exit(1)

    fsa.sample_data_peaks_raw = peaks_dataframe
    fsa.identified_sample_data_peaks = identified_peaks
    fsa.found_peaks = "agnostic"

    return fsa


def read_custom_peaks(custom_peaks):
    custom_peaks = (
        custom_peaks.fillna(0)
        if isinstance(custom_peaks, pd.DataFrame)
        else pd.read_csv(custom_peaks).fillna(0)
        if isinstance(custom_peaks, str)
        else None
    )
    if not isinstance(custom_peaks, pd.DataFrame):
        # TODO: CHANGE
        print("No custom peaks could be read")
        exit(1)

    return custom_peaks


def custom_peaks_are_overlapping(custom_peaks):
    df = read_custom_peaks(custom_peaks)
    test = (
        df.sort_values("start")
        .assign(intervals=lambda x: [range(y.start, y.stop) for y in x.itertuples()])
        .explode("intervals")
    )

    if test.shape[0] != test.intervals.nunique():
        dups = (
            test.value_counts("intervals")
            .reset_index()
            .sort_values("intervals")
            .loc[lambda x: x["count"] > 1]
            .iloc[0, 0]
        )
        print_fail(
            f"Custom peaks contains overlapping ranges starting at value: {dups}"
        )
        sys.exit(1)


def custom_peaks_has_columns(custom_peaks):
    df = read_custom_peaks(custom_peaks)

    columns = set(
        ["name", "start", "stop", "amount", "min_ratio", "which", "peak_distance"]
    )
    df_columns = set(df.columns)
    if len(columns) != len(df_columns):
        print_fail(f"Customized peaks table does not contain the right columns.")
        print_fail(f"Current columns: {df_columns}, Needed columns: {columns}")
        sys.exit(1)

    intersection = columns.intersection(df_columns)
    if len(intersection) != len(df_columns):
        print_fail(f"Customized peaks table does not contain the right columns.")
        print_fail(f"Current columns: {df_columns}, Needed columns: {columns}")
        sys.exit(1)


def find_peaks_customized(
    fsa,
    custom_peaks,
    peak_height_sample_data: int,
    search_peaks_start: int,
):
    custom_peaks = read_custom_peaks(custom_peaks)

    peaks_dataframe = fsa.sample_data_with_basepairs.loc[
        lambda x: x.basepairs > search_peaks_start
    ]
    peaks_index, _ = signal.find_peaks(
        peaks_dataframe.peaks, height=peak_height_sample_data
    )

    # Filter the df to get right peaks
    identified_peaks = peaks_dataframe.iloc[peaks_index].assign(peaks_index=peaks_index)
    # Filter the above df based on the custom peaks from the user
    customized_peaks = []
    for assay in custom_peaks.itertuples():
        df = (
            identified_peaks.loc[lambda x: x.basepairs > assay.start]
            .loc[lambda x: x.basepairs < assay.stop]
            .assign(assay=assay.name)
        )

        # Rank the peaks by height and filter out the smallest ones
        if assay.amount != 0:
            if assay.which == "LARGEST" or assay.which == "":
                df = (
                    df.assign(max_peak=lambda x: x.peaks.max())
                    .assign(ratio=lambda x: x.peaks / x.max_peak)
                    .loc[lambda x: x.ratio > assay.min_ratio]
                    .assign(rank_peak=lambda x: x.peaks.rank(ascending=False))
                    .loc[lambda x: x.rank_peak <= assay.amount]
                    .drop(columns=["rank_peak"])
                )
                if assay.peak_distance != 0:
                    df = (
                        df.assign(distance=lambda x: x.basepairs.diff())
                        .assign(distance=lambda x: x.distance.fillna(0))
                        .loc[lambda x: x.distance <= assay.peak_distance]
                        .drop(columns=["distance"])
                    )

            elif assay.which == "FIRST":
                df = (
                    df.assign(max_peak=lambda x: x.peaks.max())
                    .assign(ratio=lambda x: x.peaks / x.max_peak)
                    .loc[lambda x: x.ratio > assay.min_ratio]
                    .sort_values("basepairs", ascending=True)
                    .head(assay.amount)
                )
                if assay.peak_distance != 0:
                    df = (
                        df.assign(distance=lambda x: x.basepairs.diff())
                        .assign(distance=lambda x: x.distance.fillna(0))
                        .loc[lambda x: x.distance <= assay.peak_distance]
                        .drop(columns=["distance"])
                    )
            else:
                print("[ERROR]: column `which` must be `FIRST` or `LARGEST`")
                exit(1)

        customized_peaks.append(df)

    identified_peaks = (
        pd.concat(customized_peaks)
        .reset_index()
        .assign(peak_name=lambda x: range(1, x.shape[0] + 1))
    )

    if identified_peaks.shape[0] == 0:
        # TODO: REWRITE
        print("No peaks could be found")
        exit(1)

    fsa.sample_data_peaks_raw = peaks_dataframe
    fsa.identified_sample_data_peaks = identified_peaks
    fsa.found_peaks = "custom_peaks"

    return fsa


### PEAK AREA ###
def find_peak_widths(fsa, rel_height: float = 0.95):
    widths = signal.peak_widths(
        fsa.sample_data_peaks_raw.peaks,
        fsa.identified_sample_data_peaks.peaks_index,
        rel_height=rel_height,
    )

    df = pd.DataFrame(widths).T
    df.columns = ["x", "peak_height", "peak_start", "peak_end"]

    peak_widths = (
        df.assign(peak_start=lambda x: np.floor(x.peak_start).astype(int))
        .assign(peak_end=lambda x: np.ceil(x.peak_end).astype(int))
        .assign(peak_name=lambda x: range(1, x.shape[0] + 1))
        .merge(fsa.identified_sample_data_peaks, on="peak_name")
    )

    fsa.sample_data_peak_widths = peak_widths
    return fsa


def find_peaks_with_padding(fsa, padding: int = 4):
    # add some padding to the left and right to be sure to
    # include everything in the peak
    df = fsa.sample_data_peak_widths
    divided_peak_widths = [df.loc[df.assay == x] for x in df.assay.unique()]
    peaks_with_padding = []
    for assay in divided_peak_widths:
        whole_peaks = [
            (
                fsa.sample_data_peaks_raw.iloc[
                    x.peak_start - padding : x.peak_end + padding
                ]
                .assign(assay=x.assay)
                .assign(peak_name=x.peak_name)
            )
            for x in assay.itertuples()
        ]
        whole_peaks = pd.concat(whole_peaks)
        peaks_with_padding.append(whole_peaks)

    fsa.peaks_with_padding = pd.concat(peaks_with_padding)
    return fsa


def fit_lmfit_model_to_area(fsa, peak_finding_model: str):
    if peak_finding_model == "gauss":
        model = GaussianModel()
    elif peak_finding_model == "voigt":
        model = VoigtModel()
    elif peak_finding_model == "lorentzian":
        model = LorentzianModel()
    else:
        raise NotImplementedError(
            f"""
            {peak_finding_model} is not implemented! 
            Options: [gauss, voigt, lorentzian]
            """
        )

    fitted_peaks = []
    for a in fsa.peaks_with_padding.assay.unique():
        assay = fsa.peaks_with_padding.loc[lambda x: x.assay == a]
        for p in assay.peak_name.unique():
            peak_df = assay.loc[lambda x: x.peak_name == p]
            y = peak_df.peaks.to_numpy()
            x = peak_df.time.to_numpy()
            params = model.guess(y, x)
            out = model.fit(y, params, x=x)

            fitted_peak = peak_df.assign(
                fitted=out.best_fit,
                model=peak_finding_model,
                amplitude=out.values["amplitude"],
                center=out.values["center"],
                sigma=out.values["sigma"],
                fwhm=out.values["fwhm"],
                fit_report=out.fit_report(),
                r_value=float(
                    re.findall(r"R-squared *= (0\.\d{3})", out.fit_report())[0]
                ),
            )
            fitted_peaks.append(fitted_peak)

    fsa.fitted_area_peaks = pd.concat(fitted_peaks)
    return fsa


def calculate_quotients(fsa):
    quotients = []
    for a in fsa.fitted_area_peaks.assay.unique():
        assay = fsa.fitted_area_peaks.loc[lambda x: x.assay == a]
        df = (
            assay[["assay", "peak_name", "amplitude", "basepairs"]]
            .assign(basepairs=lambda x: x.iloc[0, -1])
            .drop_duplicates()
        )

        wide = df.pivot_wider(
            index=["assay", "basepairs"],
            names_from=["peak_name"],
            values_from=["amplitude"],
        )

        if wide.shape[1] > 4:
            quotient = wide.assign(
                quotient=lambda x: x.iloc[0, -1] / x.iloc[0, 2:4].mean()
            ).quotient.squeeze()
        elif wide.shape[1] == 3:
            quotient = 0
        else:
            quotient = wide.assign(
                quotient=lambda x: x.iloc[0, 3] / x.iloc[0, 2]
            ).quotient.squeeze()
        assay = assay.assign(quotient=quotient)
        quotients.append(assay)

    fsa.fitted_area_peaks = pd.concat(quotients)
    return fsa


def update_identified_sample_data_peaks(fsa):
    a = fsa.identified_sample_data_peaks
    b = fsa.fitted_area_peaks[["assay", "model", "r_value", "quotient"]]

    a = a.merge(b).drop_duplicates("time")
    fsa.identified_sample_data_peaks = a
    return fsa


def cli():
    parser = argparse.ArgumentParser(
        description="Analyze your Fragment analysis files!"
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        required=True,
        choices=["area", "peak"],
        help="Fraggler area or fraggler peak",
    )
    parser.add_argument("-f", "--fsa", required=True, help="fsa file to analyze")
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output folder",
    )
    valid_ladders = [x for x in LADDERS.keys()]
    parser.add_argument(
        "-l",
        "--ladder",
        choices=valid_ladders,
        required=True,
        help="Which ladder to use",
    )
    parser.add_argument(
        "-sc",
        "--sample_channel",
        required=True,
        help="Which sample channel to use. E.g: 'DATA1', 'DATA2'...",
    )
    parser.add_argument(
        "-min_dist",
        "--min_distance_between_peaks",
        required=False,
        type=int,
        default=30,
        help="Minimum distance between size standard peaks",
    )
    parser.add_argument(
        "-min_s_height",
        "--min_size_standard_height",
        required=False,
        type=int,
        default=100,
        help="Minimun height of size standard peaks",
    )
    parser.add_argument(
        "-cp",
        "--custom_peaks",
        required=False,
        default=None,
        type=str,
        help="csv file with custom peaks to find",
    )
    parser.add_argument(
        "-height_sample",
        "--peak_height_sample_data",
        required=False,
        default=300,
        type=int,
        help="Minimum height of peaks in sample data",
    )
    parser.add_argument(
        "-min_ratio",
        "--min_ratio_to_allow_peak",
        required=False,
        default=0.15,
        type=float,
        help="Minimum ratio of the lowest peak compared to the heighest peak in the assay",
    )
    parser.add_argument(
        "-distance",
        "--distance_between_assays",
        required=False,
        default=15,
        type=int,
        help="Minimum distance between assays in a multiple assay experiment",
    )
    parser.add_argument(
        "-peak_start",
        "--search_peaks_start",
        required=False,
        default=115,
        type=int,
        help="Where to start searching for peaks in basepairs",
    )
    parser.add_argument(
        "-m",
        "--peak_area_model",
        required=False,
        default="gauss",
        choices=["gauss", "voigt", "lorentzian"],
        type=str,
        help="Which peak finding model to use",
    )

    args = parser.parse_args()

    print(ASCII_ART)
    command = "\nfraggler \n" + "".join(f"{k}: {v}\n" for k, v in vars(args).items())
    print_green(command)

    main(
        command,
        sub_command=args.type,
        fsa=args.fsa,
        output=args.output,
        ladder=args.ladder,
        sample_channel=args.sample_channel,
        min_distance_between_peaks=args.min_distance_between_peaks,
        min_size_standard_height=args.min_size_standard_height,
        custom_peaks=args.custom_peaks,
        peak_height_sample_data=args.peak_height_sample_data,
        min_ratio_to_allow_peak=args.min_ratio_to_allow_peak,
        distance_between_assays=args.distance_between_assays,
        search_peaks_start=args.search_peaks_start,
        peak_area_model=args.peak_area_model,
    )


def write_log(file, *text):
    with open(file, "a+") as f:
        for line in text:
            print(line, file=f)


def read_valid_csv(csv):
    try:
        df = pd.read_csv(csv)
        return df
    except:
        print_fail(f"{csv} cannot be read!")
        sys.exit(1)


def parse_fsa(
    fsa,
    ladder,
    sample_channel,
    min_distance_between_peaks,
    min_size_standard_height,
):
    try:
        fsa = FsaFile(
            fsa,
            ladder,
            sample_channel=sample_channel,
            min_distance_between_peaks=min_distance_between_peaks,
            min_size_standard_height=min_size_standard_height,
        )
        return fsa
    except:
        print_fail(f"Cannot parse {fsa}")
        sys.exit(1)


### REPORT ###
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
        # Fraggler Report
        ## Report of {name}
        ## Date: {date}
        """,
        fontsize="20px",
        bg_color="#03a1fc",
        height=250,
    )


def generate_peak_report(fsa):
    ### ----- Raw Data ----- ###
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

    ### ----- Peaks ----- ###
    peaks_header = header(
        text="## Plot of Peaks",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )

    # PLOT
    peaks_plot = plot_all_found_peaks(fsa)
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
    ladder_plot = plot_size_standard_peaks(fsa)
    ladder_peak_plot = pn.pane.Matplotlib(
        ladder_plot,
        name="Ladder Peak Plot",
    )
    # Ladder Correlation
    model_fit = plot_model_fit(fsa)
    ladder_correlation_plot = pn.pane.Matplotlib(
        model_fit,
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
    df = fsa.identified_sample_data_peaks.assign(file_name=fsa.file_name)[
        ["basepairs", "assay", "peak_name", "file_name"]
    ]
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

    file_name = fsa.file_name
    date = fsa.fsa["RUND1"]
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


def generate_area_report(fsa):

    ### ----- Raw Data ----- ###
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

    ### ----- Peaks ----- ###
    peaks_header = header(
        text="## Plot of Peaks",
        bg_color="#04c273",
        height=80,
        textalign="left",
    )

    # PLOT
    peaks_plot = plot_all_found_peaks(fsa)
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
    ladder_plot = plot_size_standard_peaks(fsa)
    ladder_peak_plot = pn.pane.Matplotlib(
        ladder_plot,
        name="Ladder Peak Plot",
    )
    # Ladder Correlation
    model_fit = plot_model_fit(fsa)
    ladder_correlation_plot = pn.pane.Matplotlib(
        model_fit,
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
    area_plots_list = plot_areas(fsa)
    for i, plot in enumerate(area_plots_list):
        name = f"Assay {i + 1}"
        plot_pane = pn.pane.Matplotlib(plot, name=name)
        areas_tab.append(plot_pane)

    # Section
    areas_section = pn.Column(areas_header, areas_tab)

    ### ----- Peaks DataFrame ----- ###
    dataframe_header = header(
        text="## Peaks Table", bg_color="#04c273", height=80, textalign="left"
    )

    df = fsa.identified_sample_data_peaks[
        ["basepairs", "assay", "peak_name", "model", "r_value", "quotient"]
    ]

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
    file_name = fsa.file_name
    date = fsa.fsa["RUND1"]
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


def generate_no_peaks_report(fsa):
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


def main(
    command,
    sub_command,
    fsa,
    output,
    ladder,
    sample_channel,
    min_distance_between_peaks,
    min_size_standard_height,
    custom_peaks,
    peak_height_sample_data,
    min_ratio_to_allow_peak,
    distance_between_assays,
    search_peaks_start,
    peak_area_model,
):
    FAILED_FILES = []
    PEAK_TABLES = []
    start_time = datetime.now()
    print_green(f"Running fraggler {sub_command}!")

    folder_exists(output)
    make_dir(output)

    LOG_FILE = f"{output}/fraggler.log"
    write_log(LOG_FILE, "Command:", command)

    fsa_files = get_files(fsa)

    for fsa in fsa_files:
        print_green(f"Running fraggler on {fsa}")
        write_log(LOG_FILE, f"Parsing {fsa}:")
        fsa = parse_fsa(
            fsa,
            ladder,
            sample_channel=sample_channel,
            min_distance_between_peaks=min_distance_between_peaks,
            min_size_standard_height=min_size_standard_height,
        )

        print_green(f"Using size standard channel: {fsa.size_standard_channel}")
        write_log(LOG_FILE, f"Size standard channel: {fsa.size_standard_channel}")

        fsa = find_size_standard_peaks(fsa)
        fsa = return_maxium_allowed_distance_between_size_standard_peaks(
            fsa, multiplier=2
        )
        fsa = generate_combinations(fsa)
        fsa = calculate_best_combination_of_size_standard_peaks(fsa)

        if fsa.best_size_standard_combinations.shape[0] == 0:
            write_log(
                LOG_FILE,
                "No combinations of the size standard could be made",
                "Aborting",
            )
            print_fail("No combinations of the size standard could be made")
            print_warning(f"Generating a report of the raw data, please have a look...")
            no_peaks_report = generate_no_peaks_report(fsa)
            no_peaks_report.save(f"{output}/{fsa.file_name}_fraggler_fail.html")
            print_warning(f"Continuing to the next file...")
            FAILED_FILES.append(fsa.file_name)
            continue
            # sys.exit(1)

        fsa = fit_size_standard_to_ladder(fsa)

        if custom_peaks:
            print_green(f"Using custom peaks")
            # test if custom peaks are ok
            custom_peaks = read_valid_csv(custom_peaks)
            custom_peaks_are_overlapping(custom_peaks)
            custom_peaks_has_columns(custom_peaks)
            fsa = find_peaks_customized(
                fsa,
                custom_peaks,
                peak_height_sample_data=peak_height_sample_data,
                search_peaks_start=search_peaks_start,
            )
        else:  # find peak agnostic
            print_green(f"Finding peaks agnostic")
            fsa = find_peaks_agnostic(
                fsa,
                peak_height_sample_data=peak_height_sample_data,
                min_ratio=min_ratio_to_allow_peak,
                distance_between_assays=distance_between_assays,
                search_peaks_start=search_peaks_start,
            )

        print_green(f"Found {fsa.identified_sample_data_peaks.assay.nunique()} assays")
        print_green(f"Found {fsa.identified_sample_data_peaks.shape[0]} peaks")
        write_log(
            LOG_FILE,
            f"Found {fsa.identified_sample_data_peaks.assay.nunique()} assays",
            f"Found {fsa.identified_sample_data_peaks.shape[0]} peaks",
        )

        if sub_command == "peak":
            # save csv
            peak_table = fsa.identified_sample_data_peaks.assign(
                file_name=fsa.file_name
            )
            PEAK_TABLES.append(peak_table)

            # create  peak report
            print_green("Creating peak report...")
            report = generate_peak_report(fsa)
            report.save(f"{output}/{fsa.file_name}_fraggler_report.html")

            print_green(f"Fraggler done for {fsa.file_name}")
            write_log(LOG_FILE, "")

        if sub_command == "area":
            fsa = find_peak_widths(fsa)
            fsa = find_peaks_with_padding(fsa)
            fsa = fit_lmfit_model_to_area(fsa, peak_area_model)
            fsa = calculate_quotients(fsa)
            fsa = update_identified_sample_data_peaks(fsa)

            # save the table of peaks
            (
                fsa.identified_sample_data_peaks[
                    ["basepairs", "assay", "peak_name", "model", "r_value", "quotient"]
                ].to_csv(f"{output}/fraggler_peaks.csv", index=False)
            )

            # create report
            print_green("Creating area report...")
            report = generate_area_report(fsa)
            report.save(f"{output}/{fsa.file_name}_fraggler_report.html")

            print_green(f"Fraggler done for {fsa.file_name}")
            write_log(LOG_FILE, "")

    # save csv file in peak report
    if sub_command == "peak":
        (
            pd.concat(PEAK_TABLES)[
                ["basepairs", "assay", "peak_name", "file_name"]
            ].to_csv(f"{output}/{fsa.file_name}_fraggler_peaks.csv", index=False)
        )

    print_green("Fraggler done!")

    if len(FAILED_FILES) > 0:
        print_warning("Following files failed:")
        for file in FAILED_FILES:
            print_warning(f"   {file}")


if __name__ == "__main__":
    cli()
    sys.exit(0)
