import logging
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_widths
from fraggler.ladder_fitting.fit_ladder_model import FitLadderModel


######### -------------------- Custom Errors ######### --------------------
class OverlappingIntervalError(Exception):
    pass


class WrongColumnsError(Exception):
    pass


######### -------------------- Validation functions ######### --------------------
def is_overlapping(df: pd.DataFrame) -> bool:
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
        logging.warning(
            f"""
        Customized peaks contains overlapping ranges
        Starting at value: {dups}
        """
        )
        return True
    return False


def has_columns(df: pd.DataFrame) -> bool:
    columns = set(
        ["name", "start", "stop", "amount", "min_ratio", "which", "peak_distance"]
    )
    df_columns = set(df.columns)

    if len(columns) != len(df_columns):
        logging.warning(
            f"""
        Customized peaks table does not contain the right columns.
        Current columns: {df_columns}
        Needed columns: {columns}
        """
        )
        return False

    intersection = columns.intersection(df_columns)
    if len(intersection) != len(df_columns):
        logging.warning(
            f"""
        Customized peaks table does not contain the right columns.
        Current columns: {df_columns}
        Needed columns: {columns}
        """
        )
        return False

    return True


#### ---------------------------------------------------------------------------------- ###


class PeakFinder:
    def __init__(
        self,
        model: FitLadderModel,
        min_ratio: float = 0.15,
        search_peaks_start: int = 110,
        peak_height: int = 350,
        distance_between_assays: int = 15,
        custom_peaks: str | pd.DataFrame = None,
    ) -> None:
        self.model = model
        self.raw_data = self.model.adjusted_baisepair_df
        self.file_name = self.model.fsa_file.file_name
        self.search_peaks_start = search_peaks_start
        self.peak_height = peak_height
        self.min_ratio = min_ratio
        self.distance_between_assays = distance_between_assays
        self.custom_peaks = (
            custom_peaks.fillna(0)
            if isinstance(custom_peaks, pd.DataFrame)
            else pd.read_csv(custom_peaks).fillna(0)
            if isinstance(custom_peaks, str)
            else None
        )

        # Validation of custom_peaks
        self.run_validation()
        # find peaks, custom or agnostic
        self.find_peaks()
        # continue whether peaks are found or not.
        self.found_peaks()

    def run_validation(self):
        if self.custom_peaks is None:
            return

        if is_overlapping(self.custom_peaks):
            raise OverlappingIntervalError("Overlapping intervals!")
            exit(1)

        if not has_columns(self.custom_peaks):
            raise WrongColumnsError("Wrong columns!")
            exit(1)

    def find_peaks(self):
        if self.custom_peaks is not None:
            self.find_peaks_customized(
                peak_height=self.peak_height,
            )
        else:
            self.find_peaks_agnostic(
                peak_height=self.peak_height,
                min_ratio=self.min_ratio,
                distance_between_assays=self.distance_between_assays,
            )

    def found_peaks(self):
        # if no peaks could be found
        if self.peak_information.shape[0] == 0:
            self.found_peaks = False
            logging.warning(f"No peaks could be found. Please look at raw data.")
        # if peaks are found
        else:
            self.found_peaks = True

    def find_peaks_agnostic(
        self,
        peak_height: int,
        min_ratio: float,
        distance_between_assays: int,
    ) -> None:
        peaks_dataframe = self.raw_data.loc[
            lambda x: x.basepairs > self.search_peaks_start
        ]
        peaks_index, _ = find_peaks(peaks_dataframe.peaks, height=peak_height)

        peak_information = (
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

        # update peaks_index based on the above filtering
        peaks_index = peak_information.peaks_index.to_numpy()

        # update class attributes
        self.peaks_index = peaks_index
        self.peaks_dataframe = peaks_dataframe
        self.peak_information = peak_information

    def find_peaks_customized(
        self,
        peak_height: int,
    ) -> None:

        # Filter where to start search for the peaks
        peaks_dataframe = self.raw_data.loc[
            lambda x: x.basepairs > self.search_peaks_start
        ]
        # Find the peaks
        peaks_index, _ = find_peaks(peaks_dataframe.peaks, height=peak_height)

        # Filter the df to get right peaks
        peak_information = peaks_dataframe.iloc[peaks_index].assign(
            peaks_index=peaks_index
        )
        # Filter the above df based on the custom peaks from the user
        customized_peaks = []
        for assay in self.custom_peaks.itertuples():
            df = (
                peak_information.loc[lambda x: x.basepairs > assay.start]
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

        peak_information = (
            pd.concat(customized_peaks)
            .reset_index()
            .assign(peak_name=lambda x: range(1, x.shape[0] + 1))
        )

        # update peaks_index based on the above filtering
        peaks_index = peak_information.peaks_index.to_numpy()

        # update class attributes
        self.peaks_index = peaks_index
        self.peaks_dataframe = peaks_dataframe
        self.peak_information = peak_information
