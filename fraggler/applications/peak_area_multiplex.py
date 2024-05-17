import logging
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lmfit.models import VoigtModel, GaussianModel, LorentzianModel
from scipy.signal import find_peaks, peak_widths
from ..utils.peak_finder import PeakFinder


class PeakAreaDeMultiplexIterator:
    def __init__(self, number_of_assays):
        self.number_of_assays = number_of_assays
        self.current = 0

    def __next__(self):
        if self.current >= self.number_of_assays:
            raise StopIteration
        result = self.current
        self.current += 1
        return result


class PeakAreaDeMultiplex:
    def __init__(
        self,
        peaks: PeakFinder,
        cutoff: float = None,
    ) -> None:
        self.peaks = peaks
        self.cutoff = cutoff or None
        self.peaks_dataframe = self.peaks.peaks_dataframe
        self.peak_information = self.peaks.peak_information
        self.file_name = self.peaks.file_name
        self.peaks_index = self.peaks.peaks_index
        self.found_peaks = self.peaks.found_peaks
        self.area_plots = []

        self.find_peak_widths()
        # divade peaks based on their assay they belonging
        self.divided_assays = self.divide_peak_assays()
        # how many assays does this sample contain?
        self.number_of_assays = len(self.divided_assays)
        # divide all peaks in each assay into separate dataframes
        self.divided_peaks = [self.divide_peaks(x) for x in self.divided_assays]
        # logging
        logging.info(
            f"""
        Number of assays found: {self.number_of_assays}
        Number of peaks found: {self.peak_information.shape[0]}
        """
        )

    def __iter__(self):
        return PeakAreaDeMultiplexIterator(self.number_of_assays)

    def find_peak_widths(self, rel_height: float = 0.95):
        widths = peak_widths(
            self.peaks_dataframe.peaks,
            self.peaks_index,
            rel_height=rel_height,
        )

        df = pd.DataFrame(widths).T
        df.columns = ["x", "peak_height", "peak_start", "peak_end"]

        self.peak_widths = (
            df.assign(peak_start=lambda x: np.floor(x.peak_start).astype(int))
            .assign(peak_end=lambda x: np.ceil(x.peak_end).astype(int))
            .assign(peak_name=lambda x: range(1, x.shape[0] + 1))
            .merge(self.peak_information, on="peak_name")
        )

    def divide_peak_assays(self) -> list[pd.DataFrame]:
        """
        Divide the peaks belonging to different assays based on their assay number
        """
        df = self.peak_widths
        return [df.loc[df.assay == x] for x in df.assay.unique()]

    def divide_peaks(self, assay: pd.DataFrame, padding: int = 4) -> list[pd.DataFrame]:
        # add some padding to the left and right to be sure to include everything in the peak
        return [
            self.peaks_dataframe.iloc[x.peak_start - padding : x.peak_end + padding]
            for x in assay.itertuples()
        ]

    def fit_lmfit_model(self, peak_finding_model: str, assay_number: int):
        if assay_number >= self.number_of_assays:
            raise IndexError(
                f"""
                The sample only contains {self.number_of_assays} assays. 
                Use a number inside of the range.
                Indexing starts at 0.
                """
            )

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

        fit_df = []
        fit_params = []
        fit_report = []
        for df in self.divided_peaks[assay_number]:
            df = df.copy()
            y = df.peaks.to_numpy()
            # CHANGED to time instead of basepair
            x = df.time.to_numpy()

            params = model.guess(y, x)
            out = model.fit(y, params, x=x)

            fit_df.append(df.assign(fitted=out.best_fit, model=peak_finding_model))
            fit_params.append(out.values)
            fit_report.append(out.fit_report())

        # Update the instances of the model fit
        self.fit_df = fit_df
        self.fit_params = fit_params
        self.fit_report = fit_report

    # TODO
    # Fix so that the cutoff is a range or something else.
    def calculate_quotient(
        self,
    ) -> None:

        """
        :Params:
        """
        areas = np.array([x["amplitude"] for x in self.fit_params])

        right_by_left = (
            self.cutoff is None
            or pd.concat(self.fit_df).basepairs.mean() >= self.cutoff
        )
        # if there only is 1 peak, return 0
        if len(areas) == 1:
            self.quotient = 0
            return

        # if there only are 2 peaks, return the quotient
        if len(areas) == 2:
            # left peak divided by right peak
            if not right_by_left:
                self.quotient = areas[0] / areas[1]
                return
            # right peak divided by left peak
            self.quotient = areas[1] / areas[0]
            return

        # return the last peak divided by the mean of the peaks to the left of it
        self.quotient = areas[-1] / areas[:-1].mean()

    def peak_position_area_dataframe(
        self, assay_number: int, name: str
    ) -> pd.DataFrame:
        """
        Returns a DataFrame of each peak and its properties
        """
        dataframes = []
        for i, _ in enumerate(self.fit_df):
            report = self.fit_report[i]
            r_value = float(re.findall(r"R-squared *= (0\.\d{3})", report)[0])
            df = (
                self.fit_df[i]
                .loc[lambda x: x.peaks == x.peaks.max()]
                .assign(area=self.fit_params[i]["amplitude"])
                .assign(r_value=r_value)
                .assign(peak_name=f"Peak {i + 1}")
                .drop(columns="time")
                .reset_index(drop=True)
                .rename(
                    columns={
                        "peaks": "peak_height",
                        "fitted": "fitted_peak_height",
                    }
                )
                .drop_duplicates("peak_name")
                .assign(file_name=self.file_name)
                .assign(assay_name=name)
            )
            dataframes.append(df)

        self.assay_peak_area_df = pd.concat(dataframes).assign(
            quotient=self.quotient,
            peak_number=lambda x: x.shape[0],
            assay_number=assay_number + 1,
        )

    def plot_areas(self, peak_finding_model: str):
        fig_areas, axs = plt.subplots(
            1, len(self.fit_df), sharey=True, figsize=(20, 10)
        )
        # if there is only one peak
        if len(self.fit_df) == 1:
            axs.plot(self.fit_df[0].basepairs, self.fit_df[0].peaks, "o")
            axs.plot(self.fit_df[0].basepairs, self.fit_df[0].fitted)
            axs.set_title(f"Peak 1 area: {self.fit_params[0]['amplitude']: .1f}")
            axs.grid()
        # if more than one peak
        else:
            for i, ax in enumerate(axs):
                ax.plot(
                    self.fit_df[i].basepairs,
                    self.fit_df[i].peaks,
                    "o",
                )
                ax.plot(self.fit_df[i].basepairs, self.fit_df[i].fitted)
                ax.set_title(
                    f"Peak {i + 1} area: {self.fit_params[i]['amplitude']: .1f}"
                )
                ax.grid()

        fig_areas.suptitle(f"Quotient: {self.quotient: .2f}")
        fig_areas.legend(["Raw data", "Model"])
        fig_areas.supxlabel("basepairs")
        fig_areas.supylabel("intensity")
        plt.close()

        return fig_areas

    def fit_assay_peaks(
        self,
        peak_finding_model: str,
        assay_number: int,
        name: str,
    ) -> None:
        """
        Runs fit_lmfit_model, calculate_quotient and peak_position_area_dataframe
        """
        self.fit_lmfit_model(peak_finding_model, assay_number)
        self.calculate_quotient()
        self.peak_position_area_dataframe(assay_number, name)
        # area plots
        area_plot = self.plot_areas(peak_finding_model)
        self.area_plots.append(area_plot)
        return self.assay_peak_area_df

    def assays_dataframe(self, peak_finding_model: str = "gauss"):
        dfs = []
        for i in self:
            if self.peaks.custom_peaks is not None:
                name = self.peaks.custom_peaks.name.unique()[i]
            else:
                name = ""
            dfs.append(self.fit_assay_peaks(peak_finding_model, i, name))
        df = pd.concat(dfs, ignore_index=True)
        # initialize attribute self.final_df
        self.final_df = df
        return df
