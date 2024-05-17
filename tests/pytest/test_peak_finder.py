import pytest
import pandas as pd
import numpy as np
import fraggler
from fraggler.ladder_fitting.fit_ladder_model import FitLadderModel
from fraggler.ladder_fitting.peak_ladder_assigner import PeakLadderAssigner
from fraggler.utils.fsa_file import FsaFile, LadderNotFoundError

from fraggler.utils.peak_finder import is_overlapping, has_columns, PeakFinder


def test_is_overlapping_no_overlap():
    df = pd.DataFrame({"start": [1, 4, 8], "stop": [3, 6, 10]})
    assert not is_overlapping(df)


def test_is_overlapping_do_overlap():
    df = pd.DataFrame({"start": [1, 4, 5], "stop": [3, 6, 10]})
    assert is_overlapping(df)


def test_has_columns_correct():
    df = pd.DataFrame(
        {
            "name": [],
            "start": [],
            "stop": [],
            "amount": [],
            "min_ratio": [],
            "which": [],
            "peak_distance": [],
        }
    )
    assert has_columns(df) == True


def test_has_columns_missing_one():
    df = pd.DataFrame(
        {"name": [], "start": [], "stop": [], "amount": [], "min_ratio": []}
    )
    assert has_columns(df) == False


def test_has_columns_extra_one():
    df = pd.DataFrame(
        {
            "name": [],
            "start": [],
            "stop": [],
            "amount": [],
            "min_ratio": [],
            "which": [],
            "peak_distance": [],
            "extra": [],
        }
    )
    assert has_columns(df) == False


def test_invalid_ladder_error():
    invalid = "WRONG"
    with pytest.raises(LadderNotFoundError) as excinfo:
        fsa = FsaFile(
            file="demo/multiplex.fsa",
            ladder=invalid,
        )
    assert str(excinfo.value) == f"'{invalid}' is not a valid ladder"
