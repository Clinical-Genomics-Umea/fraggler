import pytest
import pandas as pd
import numpy as np
import fraggler


def test_custom_peaks():
    fsa_multiplex = fraggler.FsaFile(
        file="demo/multiplex.fsa",
        ladder="LIZ",
    )
    ladder_assigner_multiplex = fraggler.PeakLadderAssigner(fsa_multiplex)
    model_multiplex = fraggler.FitLadderModel(ladder_assigner_multiplex)

    # first custom peaks
    custom_peaks = pd.DataFrame(
        {
            "name": ["test1"],
            "start": [135],
            "stop": [400],
            "amount": [2],
            "min_ratio": [0.1],
            "which": ["FIRST"],
            "peak_distance": [0],
        }
    )
    pf_multiplex = fraggler.PeakFinder(model_multiplex, custom_peaks=custom_peaks)
    pam = fraggler.PeakAreaDeMultiplex(pf_multiplex)

    assert pam.peak_information.shape[0] == 2

    custom_peaks = pd.DataFrame(
        {
            "name": ["test1"],
            "start": [135],
            "stop": [400],
            "amount": [1],
            "min_ratio": [0.1],
            "which": ["FIRST"],
            "peak_distance": 0,
        }
    )

    pf_multiplex = fraggler.PeakFinder(model_multiplex, custom_peaks=custom_peaks)
    pam = fraggler.PeakAreaDeMultiplex(pf_multiplex)

    assert pam.peak_information.shape[0] == 1
    assert pam.peak_information.basepairs.round().squeeze() == 141.0

    custom_peaks = pd.DataFrame(
        {
            "name": ["test1"],
            "start": [135],
            "stop": [400],
            "amount": [1],
            "min_ratio": [0.1],
            "which": ["LARGEST"],
            "peak_distance": 0,
        }
    )

    pf_multiplex = fraggler.PeakFinder(model_multiplex, custom_peaks=custom_peaks)
    pam = fraggler.PeakAreaDeMultiplex(pf_multiplex)

    assert pam.peak_information.basepairs.round().squeeze() == 281.0

    custom_peaks = pd.DataFrame(
        {
            "name": ["test1"],
            "start": [135],
            "stop": [400],
            "amount": [10],
            "min_ratio": [0.8],
            "which": ["LARGEST"],
            "peak_distance": [0],
        }
    )

    pf_multiplex = fraggler.PeakFinder(model_multiplex, custom_peaks=custom_peaks)
    pam = fraggler.PeakAreaDeMultiplex(pf_multiplex)

    assert pam.peak_information.shape[0] == 1
