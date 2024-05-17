import pytest
import pandas as pd
import numpy as np
import fraggler


@pytest.fixture
def pam():
    fsa_multiplex = fraggler.FsaFile(
        file="demo/multiplex.fsa",
        ladder="LIZ",
    )
    ladder_assigner_multiplex = fraggler.PeakLadderAssigner(fsa_multiplex)
    model_multiplex = fraggler.FitLadderModel(ladder_assigner_multiplex)
    pf_multiplex = fraggler.PeakFinder(model_multiplex)
    pam = fraggler.PeakAreaDeMultiplex(pf_multiplex)

    return pam


def test_peak_model(pam):
    gauss = pam.fit_assay_peaks("gauss", 1, "test")
    voigt = pam.fit_assay_peaks("voigt", 1, "test")

    assert round(voigt.fitted_peak_height.to_list()[0], 1) == 731.8
    assert round(gauss.fitted_peak_height.to_list()[0], 1) == 708.3

    assert gauss.file_name.to_list()[0] == "multiplex.fsa"
    assert voigt.file_name.to_list()[0] == "multiplex.fsa"

    assert gauss.assay_name.to_list()[0] == "test"
    assert voigt.assay_name.to_list()[0] == "test"

    assert round(gauss.area.to_list()[0], 1) == 3117.4
    assert round(voigt.area.to_list()[0], 1) == 3705.6
